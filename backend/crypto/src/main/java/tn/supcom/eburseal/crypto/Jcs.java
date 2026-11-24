package tn.supcom.eburseal.crypto;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Canonisation JSON (JCS, RFC 8785) restreinte aux types signés par EburSeal :
 * objets (Map), tableaux (List), chaînes, entiers, booléens et null.
 * Les nombres à virgule sont refusés : on n'en signe jamais.
 */
public final class Jcs {

    private static final long ENTIER_MAX = 9_007_199_254_740_991L;   // 2^53 - 1

    private Jcs() {}

    public static byte[] canoniser(Object valeur) {
        StringBuilder sb = new StringBuilder();
        ecrire(valeur, sb);
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static void ecrire(Object v, StringBuilder sb) {
        switch (v) {
            case null -> sb.append("null");
            case Boolean b -> sb.append(b);
            case Integer i -> ecrireEntier(i, sb);
            case Long l -> ecrireEntier(l, sb);
            case String s -> ecrireChaine(s, sb);
            case Map<?, ?> m -> ecrireObjet(m, sb);
            case List<?> l -> ecrireTableau(l, sb);
            default -> throw new IllegalArgumentException(
                    "Type non signable : " + v.getClass().getSimpleName());
        }
    }

    private static void ecrireEntier(long n, StringBuilder sb) {
        if (n > ENTIER_MAX || n < -ENTIER_MAX) {
            throw new IllegalArgumentException("Entier hors de la plage sûre de JSON : " + n);
        }
        sb.append(n);
    }

    private static void ecrireObjet(Map<?, ?> m, StringBuilder sb) {
        TreeMap<String, Object> trie = new TreeMap<>();
        for (Map.Entry<?, ?> e : m.entrySet()) {
            if (!(e.getKey() instanceof String cle)) {
                throw new IllegalArgumentException("Clé non textuelle");
            }
            trie.put(cle, e.getValue());
        }
        sb.append('{');
        boolean premier = true;
        for (Map.Entry<String, Object> e : trie.entrySet()) {
            if (!premier) sb.append(',');
            premier = false;
            ecrireChaine(e.getKey(), sb);
            sb.append(':');
            ecrire(e.getValue(), sb);
        }
        sb.append('}');
    }

    private static void ecrireTableau(List<?> l, StringBuilder sb) {
        sb.append('[');
        for (int i = 0; i < l.size(); i++) {
            if (i > 0) sb.append(',');
            ecrire(l.get(i), sb);
        }
        sb.append(']');
    }

    private static void ecrireChaine(String s, StringBuilder sb) {
        if (!StandardCharsets.UTF_8.newEncoder().canEncode(s)) {
            throw new IllegalArgumentException("Chaîne Unicode invalide");
        }
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"'  -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\b' -> sb.append("\\b");
                case '\f' -> sb.append("\\f");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        sb.append('"');
    }
}
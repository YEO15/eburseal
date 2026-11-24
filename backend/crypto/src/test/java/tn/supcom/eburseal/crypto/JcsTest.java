package tn.supcom.eburseal.crypto;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class JcsTest {

    private static String jcs(Object v) {
        return new String(Jcs.canoniser(v), StandardCharsets.UTF_8);
    }

    @Test
    void lesClesSontTrieesEtSansEspaces() {
        assertEquals("{\"a\":2,\"b\":1}", jcs(Map.of("b", 1, "a", 2)));
    }

    @Test
    void objetsImbriquesEtTableaux() {
        Object v = Map.of("z", List.of(true, "x"), "a", Map.of("d", 1, "c", 2));
        assertEquals("{\"a\":{\"c\":2,\"d\":1},\"z\":[true,\"x\"]}", jcs(v));
    }

    @Test
    void echappementsConformesALaRfc() {
        assertEquals("\"a\\\"b\\\\c\\n\\u0001é\"", jcs("a\"b\\c\n\u0001é"));
    }

    /** Exemple de tri de la RFC 8785 §3.2.3 : ordre des unités UTF-16, pas des points de code. */
    @Test
    void triParUnitesUtf16CommeLaRfc() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("\u20ac", 1);          // €
        m.put("\r", 2);
        m.put("\ufb33", 3);
        m.put("1", 4);
        m.put("\ud83d\ude00", 5);    // emoji 😀
        m.put("\u0080", 6);
        m.put("\u00f6", 7);          // ö
        assertEquals("{\"\\r\":2,\"1\":4,\"\u0080\":6,\"\u00f6\":7,\"\u20ac\":1,\"\ud83d\ude00\":5,\"\ufb33\":3}",
                jcs(m));
    }

    @Test
    void lesNombresAVirguleSontRefuses() {
        assertThrows(IllegalArgumentException.class, () -> jcs(Map.of("x", 1.5)));
    }

    @Test
    void lesEntiersHorsPlageSontRefuses() {
        assertThrows(IllegalArgumentException.class, () -> jcs(9_007_199_254_740_992L));
    }
}
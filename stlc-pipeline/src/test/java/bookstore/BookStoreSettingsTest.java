package bookstore;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class BookStoreSettingsTest {
    private Map<String, String> environment() {
        return new HashMap<>(Map.of(
            "BOOK_STORE_URL", "https://example.test/books",
            "BOOK_STORE_SEARCH_INPUT", "#search",
            "BOOK_STORE_SEARCH_BUTTON", "#submit",
            "BOOK_STORE_DETAIL_CONTAINER", ".details",
            "BOOK_STORE_EMPTY_MESSAGE", ".empty",
            "BOOK_STORE_EXPECTED_DETAILS", "Expected author"
        ));
    }

    @Test
    void requiresActualTargetConfiguration() {
        Map<String, String> values = environment();
        values.remove("BOOK_STORE_URL");
        assertEquals("BOOK_STORE_URL must be configured before running book-search tests",
            assertThrows(IllegalArgumentException.class, () -> BookStoreSettings.from(values)).getMessage());
    }

    @Test
    void refusesNonHttpTargets() {
        Map<String, String> values = environment();
        values.put("BOOK_STORE_URL", "file:///local/page.html");
        assertEquals("BOOK_STORE_URL must use http or https",
            assertThrows(IllegalArgumentException.class, () -> BookStoreSettings.from(values)).getMessage());
    }

    @Test
    void acceptsConfiguredTarget() {
        BookStoreSettings settings = BookStoreSettings.from(environment());
        assertEquals("#search", settings.searchInput());
        assertEquals("Expected author", settings.expectedDetails());
    }
}

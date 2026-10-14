package bookstore;

import java.net.URI;
import java.util.Map;

record BookStoreSettings(
    URI url,
    String searchInput,
    String searchButton,
    String detailContainer,
    String emptyMessage,
    String expectedDetails
) {
    static BookStoreSettings from(Map<String, String> environment) {
        URI url = URI.create(required(environment, "BOOK_STORE_URL"));
        if (!"http".equalsIgnoreCase(url.getScheme()) && !"https".equalsIgnoreCase(url.getScheme())) {
            throw new IllegalArgumentException("BOOK_STORE_URL must use http or https");
        }
        if (url.getHost() == null) {
            throw new IllegalArgumentException("BOOK_STORE_URL must have a host");
        }
        return new BookStoreSettings(
            url,
            required(environment, "BOOK_STORE_SEARCH_INPUT"),
            required(environment, "BOOK_STORE_SEARCH_BUTTON"),
            required(environment, "BOOK_STORE_DETAIL_CONTAINER"),
            required(environment, "BOOK_STORE_EMPTY_MESSAGE"),
            required(environment, "BOOK_STORE_EXPECTED_DETAILS")
        );
    }

    private static String required(Map<String, String> environment, String name) {
        String value = environment.get(name);
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " must be configured before running book-search tests");
        }
        return value.trim();
    }
}

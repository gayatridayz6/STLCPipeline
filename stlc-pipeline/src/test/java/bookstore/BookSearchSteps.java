package bookstore;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class BookSearchSteps {
    private BookStoreSettings settings;
    private WebDriver driver;
    private WebDriverWait wait;

    @Before
    public void openBrowser() {
        settings = BookStoreSettings.from(System.getenv());
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @After
    public void closeBrowser() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Given("the user is on the book store homepage")
    public void userIsOnHomepage() {
        driver.get(settings.url().toString());
    }

    @When("the user searches for {string}")
    public void searchFor(String title) {
        WebElement input = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(settings.searchInput())));
        input.clear();
        input.sendKeys(title);
        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(settings.searchButton()))).click();
    }

    @Then("the book details for {string} are displayed")
    public void detailsAreDisplayed(String title) {
        WebElement details = wait.until(
            ExpectedConditions.visibilityOfElementLocated(By.cssSelector(settings.detailContainer()))
        );
        String displayed = details.getText();
        assertTrue(displayed.contains(title), "Book details must include the requested title");
        assertTrue(displayed.contains(settings.expectedDetails()), "Book details must include the configured fixture detail");
    }

    @Then("the message {string} is displayed")
    public void noBooksFound(String message) {
        WebElement empty = wait.until(
            ExpectedConditions.visibilityOfElementLocated(By.cssSelector(settings.emptyMessage()))
        );
        assertEquals(message, empty.getText().trim());
        assertTrue(driver.findElements(By.cssSelector(settings.detailContainer())).stream()
            .noneMatch(WebElement::isDisplayed), "No book details should be visible for an unknown title");
    }
}

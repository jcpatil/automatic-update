import time
import os
import sys
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
LOGIN_URL = "https://www.naukri.com/nlogin/login"

# USER CREDENTIALS
# Load environment variables
load_dotenv()

USERNAME = os.getenv("NAUKRI_USERNAME")
PASSWORD = os.getenv("NAUKRI_PASSWORD")

if not USERNAME or not PASSWORD:
    print("Error: NAUKRI_USERNAME or NAUKRI_PASSWORD not found in environment variables.")
    print("Please ensure a .env file exists with these keys.")
    sys.exit(1)

def get_driver():
    """Initialize undetected Chrome driver to bypass bot detection"""
    options = uc.ChromeOptions()
    
    # Essential options for GitHub Actions
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Aggressive stealth parameters
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--window-size=1920,1080")
    
    # Spoof user agent to look like a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")
    
    # Use undetected-chromedriver with headless mode
    # undetected-chromedriver already patches most automation detection automatically
    driver = uc.Chrome(
        options=options,
        headless=True,
        use_subprocess=False,
        version_main=144  # Match Chrome 144.x on GitHub Actions
    )
    
    return driver

def login_to_naukri(driver):
    print("Attempting to log in...")
    driver.get(LOGIN_URL)
    time.sleep(3)
    
    try:
        wait = WebDriverWait(driver, 10)
        email_field = wait.until(EC.visibility_of_element_located((By.ID, "usernameField")))
        email_field.clear()
        email_field.send_keys(USERNAME)
        
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
        login_button.click()
        
        print("Login credentials accepted. Waiting for redirect...")
        wait.until(EC.url_contains("mnjuser/profile"))
        print("Login successful!")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def update_resume_headline(driver):
    print("Navigating to profile...")
    driver.get(PROFILE_URL)
    wait = WebDriverWait(driver, 25)

    # Check for login redirection or if we are merely at the dashboard
    # The user screenshot shows they are at the dashboard (home page), so we might need to force navigation
    if "login" in driver.current_url or "naukri.com/mnjuser/homepage" in driver.current_url:
        print("Not on profile page. Checking login...")
        
        # If explicitly at login page, do the login dance
        if "login" in driver.current_url:
             if not login_to_naukri(driver):
                return False
        
    # CRITICAL FIX: After login (or if we were just on homepage), GO TO PROFILE
        print("Navigating to Profile Page explicitly...")
        driver.get(PROFILE_URL)
        time.sleep(5) # Increased wait

    try:
        print(f"DEBUG: Current URL: {driver.current_url}")
        
        # CRITICAL: Wait for page to fully load with explicit waits
        print("DEBUG: Waiting for page to fully load...")
        time.sleep(8)  # Give extra time for JavaScript to load
        
        # Verify we're logged in by checking for profile indicators
        try:
            # Look for common profile indicators (name, profile completeness, etc.)
            profile_indicators = driver.find_elements(By.XPATH, "//*[contains(@class, 'name') or contains(@class, 'profile')]")
            print(f"DEBUG: Found {len(profile_indicators)} potential profile indicators")
            
            # Try to find any text content on the page
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"DEBUG: Page has {len(page_text)} characters of text")
            
            if len(page_text) < 500:
                print("WARNING: Page seems to have very little content - might not be fully loaded")
                print(f"DEBUG: First 200 chars of page: {page_text[:200]}")
        except Exception as e:
            print(f"DEBUG: Error checking page indicators: {str(e)[:100]}")
        
        # Save a screenshot to see what we're looking at
        try:
            driver.save_screenshot("before_edit_search.png")
            print("DEBUG: Saved screenshot as before_edit_search.png")
        except:
            pass
            
        print("Locating 'Resume Headline' section...")

        edit_button = None
        headline_element = None
        parent_container = None

        # STRATEGY 1: Robust Text Search + Icon Lookup
        # Locate the "Resume Headline" text first, then find the edit button nearby
        headline_selectors = [
             "//span[contains(text(), 'Resume Headline')]",
             "//span[contains(@class, 'widgetTitle') and contains(text(), 'Resume')]",
             "//*[contains(translate(text(), 'RESUME HEADLINE', 'resume headline'), 'resume headline')]",
             "//div[contains(@class, 'widgetHead')]//span[contains(text(), 'Resume')]",
             "//*[contains(text(), 'Resume')]"
        ]

        print("DEBUG: Attempting Strategy 1 - Text-based search...")
        for selector in headline_selectors:
            try:
                headline_element = driver.find_element(By.XPATH, selector)
                print(f"✓ Found 'Resume Headline' text using selector #{headline_selectors.index(selector)+1}")
                
                # Now look for the edit button nearby
                parent = headline_element.find_element(By.XPATH, "./..")
                grandparent = headline_element.find_element(By.XPATH, "./../..")
                
                button_candidates = []
                
                # Search in parent and grandparent
                for container in [parent, grandparent]:
                     # Look for known classes
                     button_candidates.extend(container.find_elements(By.CSS_SELECTOR, ".edit"))
                     button_candidates.extend(container.find_elements(By.CSS_SELECTOR, ".icon-edit"))
                     button_candidates.extend(container.find_elements(By.CSS_SELECTOR, ".naukicon-edit"))
                     button_candidates.extend(container.find_elements(By.CSS_SELECTOR, "[class*='edit-icon']"))
                     button_candidates.extend(container.find_elements(By.CSS_SELECTOR, "[class*='pencil']"))
                     button_candidates.extend(container.find_elements(By.XPATH, ".//i | .//span[contains(@class, 'icon')]"))
                
                if button_candidates:
                    print(f"DEBUG: Found {len(button_candidates)} potential edit buttons nearby")
                    for btn in button_candidates:
                        try:
                            if btn.is_displayed():
                                edit_button = btn
                                print("✓ Selected a visible edit button from Strategy 1")
                                parent_container = grandparent
                                break
                        except:
                            continue
                    if edit_button:
                        break
            except Exception as e:
                print(f"DEBUG: Selector #{headline_selectors.index(selector)+1} failed: {str(e)[:50]}")
                continue

        # STRATEGY 2: Search for ALL edit-like elements on the entire page
        if not edit_button:
            print("DEBUG: Strategy 1 failed. Attempting Strategy 2 - Global icon search...")
            
            # Cast a wide net for all possible edit buttons/icons
            all_edit_selectors = [
                ".edit",
                ".icon-edit", 
                ".naukicon-edit",
                "[class*='edit']",
                "[class*='pencil']",
                "span.edit",
                "i.edit",
                "a.edit",
                "button[class*='edit']",
                "span[class*='icon']"
            ]
            
            all_candidates = []
            for css_sel in all_edit_selectors:
                try:
                    found = driver.find_elements(By.CSS_SELECTOR, css_sel)
                    all_candidates.extend(found)
                    if found:
                        print(f"DEBUG: Found {len(found)} elements matching '{css_sel}'")
                except:
                    continue
            
            print(f"DEBUG: Total edit-like elements found: {len(all_candidates)}")
            
            # Filter for visible ones
            visible_candidates = []
            for candidate in all_candidates:
                try:
                    if candidate.is_displayed():
                        visible_candidates.append(candidate)
                except:
                    continue
            
            print(f"DEBUG: Visible edit-like elements: {len(visible_candidates)}")
            
            # Try to find one near "Resume" text or in the upper portion of the page
            if visible_candidates:
                # Prefer elements in the upper half of the page (likely profile section)
                for candidate in visible_candidates:
                    try:
                        location = candidate.location
                        if location['y'] < 1000:  # Upper portion
                            edit_button = candidate
                            print(f"✓ Selected edit button at y={location['y']}")
                            break
                    except:
                        continue
                
                # If still not found, just take the first visible one
                if not edit_button and visible_candidates:
                    edit_button = visible_candidates[0]
                    print("✓ Selected first visible edit-like element")


        if not edit_button:
            print("CRITICAL DEBUG: Could not find Edit button.")
            
            # Dump info about what we DID find
            if headline_element:
                print("Dumping HTML of found headline element parent:")
                try:
                    print(headline_element.find_element(By.XPATH, "./..").get_attribute('outerHTML'))
                except: 
                    print("Could not get parent HTML.")
            
            driver.save_screenshot("edit_button_missing.png")
            
            # Save full page source for analysis
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                
            raise Exception("Could not locate 'Edit' button nearby.")
        
        # Scroll to view
        # Using a precise scroll to center the element to avoid getting stuck under sticky headers
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
        time.sleep(1) 
        
        # Click the button
        # Using JS click to bypass "ElementClickIntercepted" errors from sticky headers/overlays
        try:
            edit_button.click()
        except:
            print("Standard click intercepted. Using JavaScript click...")
            driver.execute_script("arguments[0].click();", edit_button)
            
        print("Clicked Edit button.")
        
        # Wait for modal or inline edit
        # It seems Naukri opens a modal with a textarea
        print("Waiting for textarea to appear...")
        textarea = None
        txt_selectors = [
            (By.ID, "resumeHeadlineTxt"), 
            (By.CSS_SELECTOR, "textarea#resumeHeadlineTxt"),
            (By.XPATH, "//textarea[@placeholder='Type Resume Headline']"),
            (By.TAG_NAME, "textarea")
        ]
        
        for method, sel in txt_selectors:
            try:
                textarea = wait.until(EC.element_to_be_clickable((method, sel)))
                if textarea and textarea.is_displayed():
                    break
            except:
                continue
        
        if not textarea:
             raise Exception("Could not find visible Textarea to edit.")
             
        # Logic to update text: remove '.' if exists, else add it
        current_text = textarea.get_attribute("value")
        print(f"Current Headline: {current_text}")
        
        new_text = current_text
        if current_text.endswith("."):
            new_text = current_text.rstrip(".")
            print("Action: Removing trailing period.")
        else:
            new_text = current_text + "."
            print("Action: Adding trailing period.")
            
        # Update the textarea
        textarea.clear()
        time.sleep(0.5)
        textarea.send_keys(new_text)
        print(f"New Headline set to: {new_text}")

        # Find save button in the modal (usually sibling of textarea's container or at bottom)
        save_button = None
        save_selectors = [
            "//button[contains(text(),'Save')]",
            "//div[@class='lightbox']//button[contains(@class, 'blue-btn')]",
            "//button[normalize-space()='Save']"
        ]
        
        for xpath in save_selectors:
             try:
                 save_button = driver.find_element(By.XPATH, xpath)
                 if save_button and save_button.is_displayed(): 
                     break
             except:
                 continue

        if not save_button:
            # Last resort: find the only primary button visible
             buttons = driver.find_elements(By.TAG_NAME, "button")
             for btn in buttons:
                 if btn.is_displayed() and "Save" in btn.text:
                     save_button = btn
                     break

        if not save_button:
             raise Exception("Could not find Save button.")

        # Click Save
        # Using JS click to be safe against footer/overlays
        driver.execute_script("arguments[0].click();", save_button)
        print("Clicked Save.")
        time.sleep(3)
        print("Update Successful!")
        
        # Desktop Notification
        try:
            from plyer import notification
            notification_title = "Naukri Profile Updater"
            notification_msg = f"Headline updated successfully!\nNew: {new_text}"
            
            notification.notify(
                title=notification_title,
                message=notification_msg,
                app_name='Naukri Updater',
                timeout=10
            )
            print("Notification sent.")
        except Exception as n_err:
            print(f"Notification failed: {n_err}")
            
        return True

    except Exception as e:
        print(f"Error during update: {e}")
        driver.save_screenshot("error_screenshot.png")
        return False

def main():
    print("Starting Naukri Updater...")
    driver = None
    try:
        driver = get_driver()
        success = update_resume_headline(driver)
        if success:
            print("Profile updated successfully.")
        else:
            print("Failed to update profile.")
            # Keep browser open if failed for debugging
            # time.sleep(10) 
            
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()

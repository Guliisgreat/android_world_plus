
import os
import time
import json
from absl import logging
from android_world.env import adb_utils
from android_world.env import interface
from android_world.env import tools
from android_world.env.setup_device.apps import AppSetup
from android_world.utils import screenshot_utils


class WalmartApp(AppSetup):
    """Class for setting up Walmart app with BMOCA-style initialization.
    
    This app setup handles the complex onboarding flow including guest mode
    selection, location permissions, and UI element dismissal.
    """
    apk_names = ("/home/ligu/projects/android_world_plus/downloaded_apks/b-moca/com.walmart.android_24.19-24190029_minAPI26(arm64-v8a,armeabi-v7a,x86,x86_64)(nodpi)_apkmirror.com.apk",)
    app_name = "walmart"
    
    @classmethod
    def setup(cls, env: interface.AsyncEnv) -> None:
        """Setup Walmart app with guest mode onboarding.
        
        Args:
            env: The Android environment interface.
        """
        print(f"[WalmartApp] Starting setup for {cls.app_name}...")
        try:
            super().setup(env)
            print("[WalmartApp] ✓ Cleared app data successfully")
        except Exception as e:
            print(f"[WalmartApp] ✗ Failed to clear app data: {e}")
            raise
        
        # Launch app and handle complex onboarding flow
        print("[WalmartApp] Launching app...")
        adb_utils.launch_app(cls.app_name, env.controller)
        print("[WalmartApp] ✓ App launched successfully")
        
        
        try:
            controller = tools.AndroidToolController(env=env.controller)
            print("[WalmartApp] Created AndroidToolController")
            time.sleep(3.0)  # Wait for splash screen to load
            
            # Step 1: Click "Continue as guest" button
            print("[WalmartApp] Step 1/4: Click 'Continue as guest'...")
            try:
                controller.click_element("Continue as guest")
                time.sleep(2.0)
                print("[WalmartApp] ✓ Clicked 'Continue as guest' button")
            except ValueError as e:
                print(f"[WalmartApp] ⚠ Button not found: {e}")
            
            # Step 2: Click "Maybe later" button
            print("[WalmartApp] Step 2/4: Click 'Maybe later'...")
            try:
                controller.click_element("Maybe later")
                time.sleep(1.3)
                print("[WalmartApp] ✓ Clicked 'Maybe later' button")
            except ValueError as e:
                print(f"[WalmartApp] ⚠ Button not found: {e}")
            
            # Step 3: Click "Share precise location" button
            print("[WalmartApp] Step 3/4: Click 'Share precise location'...")
            try:
                controller.click_element("Share precise location")
                time.sleep(2.4)
                print("[WalmartApp] ✓ Clicked 'Share precise location' button")
            except ValueError as e:
                print(f"[WalmartApp] ⚠ Button not found: {e}")
            
            # Step 4: Click "While using the app" button
            print("[WalmartApp] Step 4/4: Click 'While using the app'...")
            try:
                controller.click_element("While using the app")
                time.sleep(2.7)
                print("[WalmartApp] ✓ Clicked 'While using the app' button")
            except ValueError as e:
                print(f"[WalmartApp] ⚠ Button not found: {e}")
            
            print("[WalmartApp] ✓ Onboarding flow completed successfully")
                
        except Exception as e:
            print(f"[WalmartApp] ✗ Onboarding encountered issues: {e}")
            logging.warning(
                "Walmart app setup encountered issues: %s. App may still work.",
                str(e)
            )
        finally:
            print("[WalmartApp] Closing app...")
            time.sleep(5)
            adb_utils.close_app(cls.app_name, env.controller)
            print("[WalmartApp] ✓ Setup completed")


class InstagramApp(AppSetup):
    """Class for setting up Instagram app with BMOCA-style initialization.
    
    This app setup handles the login flow and dismisses dialogs like "Save login info".
    """
    apk_names = ("/home/ligu/projects/android_world_plus/downloaded_apks/b-moca/com.instagram.android_325.0.0.35.91-372509504_minAPI28(x86_64)(nodpi)_apkmirror.com.apk",)
    app_name = "instagram"
    
    @classmethod
    def setup(cls, env: interface.AsyncEnv) -> None:
        """Setup Instagram app with login and dialog dismissal.
        
        Args:
            env: The Android environment interface.
        """
        print(f"[InstagramApp] Starting setup for {cls.app_name}...")
        
        # Load credentials from account_info.json
        account_info_path = "tmp_bmoca/asset/environments/config/account_info.json"
        username = "dummy_id"
        password = "dummy_pw"
        
        if os.path.exists(account_info_path):
            try:
                with open(account_info_path, 'r') as f:
                    account_info = json.load(f)
                    if 'instagram' in account_info:
                        username = account_info['instagram'].get('id', username)
                        password = account_info['instagram'].get('password', password)
                        print(f"[InstagramApp] Loaded credentials for user: {username}")
            except Exception as e:
                print(f"[InstagramApp] Warning: Failed to load credentials: {e}")
                print(f"[InstagramApp] Using dummy credentials")
        else:
            print(f"[InstagramApp] Warning: {account_info_path} not found, using dummy credentials")
        
        try:
            super().setup(env)
            print("[InstagramApp] ✓ Cleared app data successfully")
        except Exception as e:
            print(f"[InstagramApp] ✗ Failed to clear app data: {e}")
            raise
        
        # Grant necessary permissions
        package = adb_utils.extract_package_name(
            adb_utils.get_adb_activity(cls.app_name)
        )
        print(f"[InstagramApp] Extracted package: {package}")
        
        # Grant storage permissions that Instagram requires
        try:
            adb_utils.grant_permissions(
                package,
                "android.permission.READ_EXTERNAL_STORAGE",
                env.controller,
            )
            print("[InstagramApp] ✓ Granted READ_EXTERNAL_STORAGE permission")
        except Exception as e:
            print(f"[InstagramApp] ✗ Failed to grant READ_EXTERNAL_STORAGE: {e}")
        
        try:
            adb_utils.grant_permissions(
                package,
                "android.permission.WRITE_EXTERNAL_STORAGE",
                env.controller,
            )
            print("[InstagramApp] ✓ Granted WRITE_EXTERNAL_STORAGE permission")
        except Exception as e:
            print(f"[InstagramApp] ✗ Failed to grant WRITE_EXTERNAL_STORAGE: {e}")
        
        # Launch app and handle login flow
        print("[InstagramApp] Launching app...")
        adb_utils.launch_app(cls.app_name, env.controller)
        print("[InstagramApp] ✓ App launched successfully")
        
        # Setup screenshot directory for debugging
        screenshot_dir = ".instagram_debug_screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        try:
            controller = tools.AndroidToolController(env=env.controller)
            print("[InstagramApp] Created AndroidToolController")
            time.sleep(4.0)  # Wait for splash screen to load
            
            # Capture initial state
            try:
                path = screenshot_utils.capture_screenshot(env, screenshot_dir)
                print(f"[InstagramApp] Initial screen: {path}")
            except Exception as e:
                print(f"[InstagramApp] Failed to capture initial screenshot: {e}")
            
            # Step 1: Find and click the first EditText (username field)
            print("[InstagramApp] Step 1/3: Looking for username field...")
            attempt = 0
            username_entered = False
            while attempt < 5:
                try:
                    state = env.get_state()
                    edittexts = [elem for elem in state.ui_elements 
                                if elem.class_name and 'EditText' in elem.class_name
                                and elem.is_editable and elem.bbox_pixels is not None]
                    
                    if edittexts and len(edittexts) >= 1:
                        username_field = edittexts[0]
                        x, y = username_field.bbox_pixels.center
                        x, y = int(x), int(y)
                        print(f"[InstagramApp] Found username field at: ({x}, {y})")
                        
                        # Click the username field
                        adb_utils.tap_screen(x, y, env.controller)
                        time.sleep(0.5)
                        
                        # Enter username
                        adb_utils.type_text(username, env.controller)
                        time.sleep(0.5)
                        
                        username_entered = True
                        print("[InstagramApp] ✓ Entered username")
                        break
                except Exception as e:
                    print(f"[InstagramApp] Attempt {attempt + 1}: {e}")
                
                time.sleep(1.0)
                attempt += 1
            
            if not username_entered:
                print("[InstagramApp] ⚠ Failed to enter username")
                # Capture debug screenshot
                try:
                    path = screenshot_utils.capture_screenshot(env, screenshot_dir)
                    print(f"[InstagramApp] Debug screen: {path}")
                except Exception:
                    pass
            
            # Step 2: Find and click the second EditText (password field)
            print("[InstagramApp] Step 2/3: Looking for password field...")
            attempt = 0
            password_entered = False
            while attempt < 5:
                try:
                    state = env.get_state()
                    edittexts = [elem for elem in state.ui_elements 
                                if elem.class_name and 'EditText' in elem.class_name
                                and elem.is_editable and elem.bbox_pixels is not None]
                    
                    if edittexts and len(edittexts) >= 2:
                        password_field = edittexts[1]
                        x, y = password_field.bbox_pixels.center
                        x, y = int(x), int(y)
                        print(f"[InstagramApp] Found password field at: ({x}, {y})")
                        
                        # Click the password field
                        adb_utils.tap_screen(x, y, env.controller)
                        time.sleep(0.5)
                        
                        # Enter password
                        adb_utils.type_text(password, env.controller)
                        time.sleep(0.5)
                        
                        password_entered = True
                        print("[InstagramApp] ✓ Entered password")
                        break
                except Exception as e:
                    print(f"[InstagramApp] Attempt {attempt + 1}: {e}")
                
                time.sleep(1.0)
                attempt += 1
            
            if not password_entered:
                print("[InstagramApp] ⚠ Failed to enter password")
            
            # Step 3: Click "Log in" button
            print("[InstagramApp] Step 3/3: Looking for Log in button...")
            attempt = 0
            login_clicked = False
            while attempt < 5:
                try:
                    controller.click_element("Log in")
                    time.sleep(2.0)
                    print("[InstagramApp] ✓ Clicked Log in button")
                    login_clicked = True
                    break
                except ValueError:
                    time.sleep(1.0)
                    attempt += 1
            
            if not login_clicked:
                print("[InstagramApp] ⚠ Log in button not found")
            
            # Wait for login to complete
            time.sleep(5.0)
            
            # Step 4: Dismiss "Save login info" dialog if present
            print("[InstagramApp] Checking for Save login info dialog...")
            try:
                controller.click_element("Save")
                time.sleep(1.0)
                print("[InstagramApp] ✓ Dismissed Save login info dialog")
            except ValueError:
                print("[InstagramApp] ⚠ Save dialog not found (may not appear)")
            
            # Capture final state
            try:
                path = screenshot_utils.capture_screenshot(env, screenshot_dir)
                print(f"[InstagramApp] Final screen: {path}")
            except Exception as e:
                print(f"[InstagramApp] Failed to capture final screenshot: {e}")
            
            print("[InstagramApp] ✓ Login flow completed successfully")
                
        except Exception as e:
            print(f"[InstagramApp] ✗ Login encountered issues: {e}")
            logging.warning(
                "Instagram app setup encountered issues: %s. App may still work.",
                str(e)
            )
        finally:
            print("[InstagramApp] Closing app...")
            adb_utils.close_app(cls.app_name, env.controller)
            print("[InstagramApp] ✓ Setup completed")
            print("[InstagramApp] Note: Debug screenshots saved to .instagram_debug_screenshots/ if any issues occurred")


class WikipediaApp(AppSetup):
    """Class for setting up Wikipedia app with BMOCA-style initialization.
    
    This app setup handles the onboarding flow by clicking the skip button to reach the main interface.
    """
    apk_names = ("/home/ligu/projects/android_world_plus/downloaded_apks/b-moca/org.wikipedia_2.7.50492-r-2024-06-11-50492_minAPI21(arm64-v8a,armeabi-v7a,x86,x86_64)(nodpi)_apkmirror.com.apk",)
    app_name = "wikipedia"
    
    @classmethod
    def setup(cls, env: interface.AsyncEnv) -> None:
        """Setup Wikipedia app by skipping onboarding to reach main interface.
        
        Args:
            env: The Android environment interface.
        """
        print(f"[WikipediaApp] Starting setup for {cls.app_name}...")
        try:
            super().setup(env)
            print("[WikipediaApp] ✓ Cleared app data successfully")
        except Exception as e:
            print(f"[WikipediaApp] ✗ Failed to clear app data: {e}")
            raise
        
        # Launch app and handle onboarding flow
        print("[WikipediaApp] Launching app...")
        adb_utils.launch_app(cls.app_name, env.controller)
        print("[WikipediaApp] ✓ App launched successfully")
        
        try:
            controller = tools.AndroidToolController(env=env.controller)
            print("[WikipediaApp] Created AndroidToolController")
            time.sleep(2.0)  # Wait for splash screen to load
            
            # Click Skip button
            print("[WikipediaApp] Clicking Skip button...")
            try:
                controller.click_element("Skip")
                time.sleep(2.0)
                print("[WikipediaApp] ✓ Clicked Skip button")
            except ValueError as e:
                print(f"[WikipediaApp] ⚠ Button not found: {e}")
            
            print("[WikipediaApp] ✓ Onboarding flow completed successfully")
                
        except Exception as e:
            print(f"[WikipediaApp] ✗ Onboarding encountered issues: {e}")
            logging.warning(
                "Wikipedia app setup encountered issues: %s. App may still work.",
                str(e)
            )
        finally:
            print("[WikipediaApp] Closing app...")
            adb_utils.close_app(cls.app_name, env.controller)
            print("[WikipediaApp] ✓ Setup completed")
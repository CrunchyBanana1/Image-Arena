import os
import random
import shutil
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class ImageSelectorApp:
    def __init__(self, root, source_dir, good_dir, bad_dir):
        self.root = root
        self.source_dir = source_dir
        self.good_dir = good_dir
        self.bad_dir = bad_dir

        # Ensure the "good" and "bad" directories exist
        os.makedirs(self.good_dir, exist_ok=True)
        os.makedirs(self.bad_dir, exist_ok=True)

        # Load all images from the source directory
        self.load_images()

        # Initialize the GUI
        self.label1 = tk.Label(root)
        self.label1.pack(side=tk.LEFT, padx=10, pady=10)
        self.label2 = tk.Label(root)
        self.label2.pack(side=tk.RIGHT, padx=10, pady=10)

        # Bind keyboard events
        self.root.bind('1', self.move_image1)
        self.root.bind('2', self.move_image2)

        # Bind window resize event
        self.root.bind("<Configure>", self.resize_images)

        # Start the process
        self.next_images()

    def load_images(self):
        """Load all images from the source directory and shuffle them."""
        self.images = [os.path.join(self.source_dir, f) for f in os.listdir(self.source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        random.shuffle(self.images)

    def next_images(self):
        """Display the next pair of images or a single image if only one is left."""
        # Check if there are any images left
        if len(self.images) == 0:
            #self.handle_completion()
            return

        # If only one image is left, display it alone
        if len(self.images) == 1:
            self.image1_path = self.images.pop()
            self.image2_path = None  # No second image
            self.display_single_image()
        else:
            # Load the next two images
            self.image1_path = self.images.pop()
            self.image2_path = self.images.pop()
            self.display_images()

    def display_images(self):
        """Display the current pair of images, resized to fit the window."""
        # Ensure both labels are visible
        self.label2.pack(side=tk.RIGHT, padx=10, pady=10)

        # Get the current window size
        window_width = self.root.winfo_width() // 2 - 20  # Divide by 2 for two images, subtract padding
        window_height = self.root.winfo_height() - 20  # Subtract padding

        # Ensure dimensions are valid
        if window_width <= 0 or window_height <= 0:
            return  # Skip resizing if dimensions are invalid

        # Load and resize images
        try:
            img1 = Image.open(self.image1_path)
            img1.thumbnail((window_width, window_height))
            img_tk1 = ImageTk.PhotoImage(img1)
            self.label1.config(image=img_tk1)
            self.label1.image = img_tk1  # Keep a reference to avoid garbage collection

            img2 = Image.open(self.image2_path)
            img2.thumbnail((window_width, window_height))
            img_tk2 = ImageTk.PhotoImage(img2)
            self.label2.config(image=img_tk2)
            self.label2.image = img_tk2  # Keep a reference to avoid garbage collection
        except FileNotFoundError:
            # If an image is missing, skip it and load the next pair
            self.next_images()

    def display_single_image(self):
        """Display a single image, centered in the window."""
        # Hide the second label
        self.label2.pack_forget()

        # Get the current window size
        window_width = self.root.winfo_width() - 20  # Subtract padding
        window_height = self.root.winfo_height() - 20  # Subtract padding

        # Ensure dimensions are valid
        if window_width <= 0 or window_height <= 0:
            return  # Skip resizing if dimensions are invalid

        # Load and resize the single image
        try:
            img1 = Image.open(self.image1_path)
            img1.thumbnail((window_width, window_height))
            img_tk1 = ImageTk.PhotoImage(img1)
            self.label1.config(image=img_tk1)
            self.label1.image = img_tk1  # Keep a reference to avoid garbage collection
        except FileNotFoundError:
            # If the image is missing, skip it and handle completion
            #self.handle_completion()
            self.next_images()

    def resize_images(self, event):
        """Resize images when the window is resized."""
        if hasattr(self, 'image1_path'):
            if self.image2_path:
                self.display_images()  # Resize both images
            else:
                self.display_single_image()  # Resize the single image

    def move_image1(self, event):
        """Move the first image to 'good' and the second to 'bad' (if it exists)."""
        if self.image2_path:
            self.move_images(self.image1_path, self.image2_path)
        else:
            self.move_single_image(self.image1_path, "good")

    def move_image2(self, event):
        """Move the second image to 'good' and the first to 'bad' (if it exists)."""
        if self.image2_path:
            self.move_images(self.image2_path, self.image1_path)
        else:
            self.move_single_image(self.image1_path, "bad")

    def move_images(self, chosen_image, other_image):
        """Move the chosen image to 'good' and the other to 'bad'."""
        try:
            # Move the chosen image to the "good" folder
            shutil.move(chosen_image, os.path.join(self.good_dir, os.path.basename(chosen_image)))

            # Move the other image to the "bad" folder
            shutil.move(other_image, os.path.join(self.bad_dir, os.path.basename(other_image)))

            # Check if there are more images to process
            if len(self.images) == 0:
                self.handle_completion()  # Call handle_completion if no images are left
            else:
                self.next_images()
        except FileNotFoundError:
            # If an image is missing, skip it and proceed to the next step
            if len(self.images) == 0:
                self.handle_completion()  # Call handle_completion if no images are left

    def move_single_image(self, image_path, destination):
        """Move a single image to the specified destination ('good' or 'bad')."""
        try:
            if destination == "good":
                shutil.move(image_path, os.path.join(self.good_dir, os.path.basename(image_path)))
            else:
                shutil.move(image_path, os.path.join(self.bad_dir, os.path.basename(image_path)))

            # Check if there are more images to process
            if len(self.images) == 0:
                self.handle_completion()  # Call handle_completion if no images are left
            else:
                self.next_images()
        except FileNotFoundError:
            # If the image is missing, skip it and proceed to the next step
            if len(self.images) == 0:
                self.handle_completion()  # Call handle_completion if no images are left

    def handle_completion(self):
        """Handle the completion of all images."""
        # Ask the user if they want to move "good" images back to the source folder
        if messagebox.askyesno("Restart", "All images processed. Move 'good' images back to source folder and restart?"):
            self.move_good_images_to_source()
            self.reset_gui()  # Reset the GUI state
            self.load_images()  # Reload images from the source folder
            self.next_images()  # Start over
        else:
            self.root.destroy()  # Close the application

    def move_good_images_to_source(self):
        """Move all images from the 'good' folder back to the source folder."""
        try:
            for filename in os.listdir(self.good_dir):
                file_path = os.path.join(self.good_dir, filename)
                if os.path.isfile(file_path):
                    shutil.move(file_path, os.path.join(self.source_dir, filename))
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not move images from 'good' folder. Please check the paths.")

    def reset_gui(self):
        """Reset the GUI state to ensure both labels are visible."""
        self.label2.pack(side=tk.RIGHT, padx=10, pady=10)  # Ensure the second label is visible

def load_config():
    """Load configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.json not found in the script directory.")

    with open(config_path, "r") as f:
        config = json.load(f)

    return config

if __name__ == "__main__":
    # Load configuration
    config = load_config()

    # Define the directories
    source_directory = config.get("source_directory")
    good_directory = config.get("good_directory")
    bad_directory = config.get("bad_directory")

    if not all([source_directory, good_directory, bad_directory]):
        raise ValueError("Please ensure all directory paths are specified in config.json.")

    # Create the main window
    root = tk.Tk()
    root.title("Image Selector")
    root.geometry("800x400")  # Initial window size

    # Run the app
    app = ImageSelectorApp(root, source_directory, good_directory, bad_directory)

    # Start the main loop
    root.mainloop()
import tkinter as tk
from PIL import Image, ImageTk

class Test:
    def __init__(self):
        self.root = None
        self.count = 0

    def setup(self):
        self.root = tk.Tk()
        self.counting_button_example()

    def picture_test(self):
        img_file = Image.open('/home/clayton/Pictures/cat.jpeg')
        img = ImageTk.PhotoImage(img_file)

        label0 = tk.Label(self.root, compound=tk.CENTER, padx=10, pady=20, text='This is a test!', image=img)
        label0.pack(side='right') # Adjust the size of the window to the objects in the window
        self.root.mainloop()

    def color_label_example(self):
        tk.Label(self.root, text='Label 0', fg='red', bg='black', font='Times').pack()
        tk.Label(self.root, text='Label 1', fg='light green', bg='dark green', font='Helvetica 16 bold italic').pack()
        tk.Label(self.root, text='Label 2', fg='blue', bg='yellow', font='Verdana 10 bold').pack()
        self.root.mainloop()

    def count_label(self, label: tk.Label):
        def count():
            self.count += 1
            label.config(text=str(self.count))
            label.after(1000, count)
        count()

    def counting_button_example(self):
        self.root.title('Counting in Seconds')
        label = tk.Label(self.root, fg='light blue', bg='black', font='Times 100 bold')
        label.pack()
        self.count_label(label)
        tk.Button(self.root, text='Stop', width=25, command=self.root.destroy).pack()
        self.root.mainloop()
        
test = Test()
test.setup()
from tkinter import (
    Frame,
    Listbox,
    Scrollbar,
    X, Y,
    RIGHT,
    END,
    filedialog,
    messagebox,
    Text,
    colorchooser,
    ttk,
    NW,
    Spinbox,
    Entry,
    Label,
    Tk,
    Button,
    _default_root, simpledialog, LEFT, W, E
)

try:
    from PIL import (
        Image,
        ImageTk,
    )
except Exception as e:
    print(e)

from tkfontchooser import askfont


class TextWithScrollbar(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sb = Scrollbar(master=self)
        self._sb.pack(side=RIGHT, fill=Y)

        self._txt = Text(master=self)
        self._txt.pack(fill=X)

        self._txt.config(yscrollcommand=self._sb.set)
        self._sb.config(command=self._txt.yview)

    def insert(self, *a, **k):
        self._txt.insert(*a, **k)

    def delete(self, *a, **k):
        self._txt.delete(*a, **k)

    def ScrollToBottom(self):
        self._txt.see(END)

    def Clear(self):
        textget = self._txt.get("1.0", END)
        print('textget=', textget)
        print('len(textget)=', len(textget))
        if len(textget) > 1:
            self._txt.delete(1.0, END)


class ListboxWithScrollbar(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sb = Scrollbar(master=self)
        self._sb.pack(side=RIGHT, fill=Y)

        self._lb = Listbox(master=self)
        self._lb.pack(fill=X)

        self._lb.config(yscrollcommand=self._sb.set)
        self._sb.config(command=self._lb.yview)

        self._mouseIsOnSelf = True
        self.bind('<Enter>', self._MouseEnters)
        self.bind('<Leave>', self._MouseLeaves)

        self._lb.bind('<<ListboxSelect>>', self._ListboxSelectCallback)
        self._User_ListboxSelectCallback = None

    def _MouseEnters(self, *a, **k):
        print(self, '_MouseEnters', a, k)
        self._mouseIsOnSelf = True

    def _MouseLeaves(self, *a, **k):
        print(self, '_MouseLeaves', a, k)
        self._mouseIsOnSelf = False

    @property
    def UserSelectCallback(self):
        return self._User_ListboxSelectCallback

    @UserSelectCallback.setter
    def UserSelectCallback(self, func):
        self._User_ListboxSelectCallback = func

    def GetCurrentSelection(self):
        return self.get(self.curselection())

    def ClearSelection(self):
        self.selection_clear()

    def _ListboxSelectCallback(self, *a, **k):
        print('_ListboxSelectCallback', a, k)
        if self._mouseIsOnSelf:
            if self._User_ListboxSelectCallback is not None:
                self._User_ListboxSelectCallback(*a, **k)

    def insert(self, *args, **kwargs):
        self._lb.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._lb.delete(*args, **kwargs)

    def curselection(self, *args, **kwargs):
        print('curselection', args, kwargs)
        ret = self._lb.curselection(*args, **kwargs)
        print('ret=', ret)
        if ret == tuple():
            return 0
        else:
            return ret

    def index(self, *args, **kwargs):
        return self._lb.index(*args, **kwargs)

    def get(self, *args, **kwargs):
        print('get', args, kwargs)
        return self._lb.get(*args, **kwargs)

    def bind(self, string, callback):
        print(self, 'bind', string, callback)
        if string == '<<ListboxSelect>>':
            self._User_ListboxSelectCallback = callback
        else:
            return self._lb.bind(string, callback)

    def select_set(self, *args, **kwargs):
        return self._lb.select_set(*args, **kwargs)

    def ClearAll(self):
        while True:
            item = self.get(END)
            print('ClearAll item=', item)
            if item == '':
                break
            else:
                self.delete(END)

    def GetAll(self):
        return self.get()


global _lastImageDirectory
_lastImageDirectory = None


def GetPhotoImageFromUser():
    from persistent_variables import PersistentVariables
    global _lastImageDirectory

    filename = filedialog.askopenfilename(
        initialdir=_lastImageDirectory,
        title='Select an image',
        filetypes=(
            ("all files", "*.*"),
            ('jpeg', '*.jpg'),
            ('png', '*.png'),
            ('bmp', '*.bmp'),
        )
    )
    print('filename=', filename)
    if filename == '':  # The user probably hit Cancel
        return None

    # Save the directory and use it next time
    directory = '/'.join(filename.split('/')[:-1])
    print('directory=', directory)
    PersistentVariables().Set('_lastImageDirectory', directory)
    _lastImageDirectory = directory

    image = Image.open(filename)
    photo = ImageTk.PhotoImage(image)
    photo.filename = filename

    return photo


def GetFolder():
    global _lastImageDirectory
    if _lastImageDirectory is None:
        _lastImageDirectory = PersistentVariables().Get('_lastImageDirectory', None)
    directory = filedialog.askdirectory()
    _lastImageDirectory = directory
    print('GetFolder return', directory)
    return directory


def GetFile():
    return filedialog.askopenfilename()  # _lastImageDirectory)


def GetSaveAsFile():
    return filedialog.asksaveasfile(
        defaultextension='.json',
        filetypes=(("JSON", "*.json"), ("All Files", "*.*")),
    )


def UpdateEntryText(entry, newText):
    entry.delete(0, END)
    entry.insert(0, newText)


def ShowMessage(title, message):
    messagebox.showinfo(title, message)


def GetColor():
    return colorchooser.askcolor()


def GetFont():
    font = askfont()
    print('font=', font)
    if font:
        # spaces in the family name need to be escaped
        font['family'] = font['family'].replace(' ', '\ ')
        font_str = "%(family)s %(size)i %(weight)s %(slant)s" % font
        if font['underline']:
            font_str += ' underline'
        if font['overstrike']:
            font_str += ' overstrike'
        print('font_str=', font_str)
        return font_str


class ProgressBar(ttk.Progressbar):
    def __init__(self, root, Min, Max, Step=1):
        super().__init__(root, length=(Max - Min))
        self.callback = None

    def Step(self):
        self.step(1)  # delta)
        self.update()

        if self.callback is not None:
            self.callback()


def AskQuestion(title, question):
    # as a yes/no questions return True/False

    res = messagebox.askquestion(title, question)

    if res == 'yes':
        return True
    else:
        return False


def CanvasPhotoImage(src, width=None, height=None):
    if isinstance(src, str):
        image = Image.open(src)
    else:  # if isinstance(src, bytes):
        image = Image.fromarray(src)

    if width and height:
        image = image.resize((width, height), Image.ANTIALIAS)

    photo = ImageTk.PhotoImage(image)
    # print('CanvasPhotoImage return', photo)
    return photo


class BlankClass:
    pass


def Layout(listOfList):
    '''
    :param listOfList: [
        [lbVideoSources, (canvas, 'columnspan=2', 'rowspan=2')],
        [BlankClass],
        [BlankClass, lblFaceCount, lblFps],
    ],
    :return:
    '''

    for rowNum, _ in enumerate(listOfList):
        for colNum, item in enumerate(listOfList[rowNum]):
            if isinstance(item, tuple):
                kwargs = list(item)
                item = kwargs.pop(0)
                kwargs = dict([thing.split('=') for thing in kwargs])
                item.grid(row=rowNum, column=colNum, **kwargs)
            elif item == BlankClass:
                pass
            else:
                item.grid(row=rowNum, column=colNum)


class SpinboxWithCallback(Spinbox):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._userCallback = None
        self.bind('<FocusOut>', self.HandleFocusChange)
        self.bind('<Key>', self.HandleKeyChange)

    @property
    def ChangeCallback(self):
        return self._userCallback

    @ChangeCallback.setter
    def ChangeCallback(self, func):
        self._userCallback = func

    def HandleKeyChange(self, key):
        if key.keysym == 'enter':
            if self._userCallback:
                self._userCallback()

    def HandleFocusChange(self):
        if self._userCallback:
            self._userCallback()


class _QueryHostUserPass(simpledialog.Dialog):

    def __init__(self, title, prompt, parent=None):

        if not parent:
            parent = _default_root

        self.prompt = prompt

        super().__init__(parent, title)



    def destroy(self):
        self.entry = None
        simpledialog.Dialog.destroy(self)

    def body(self, master):

        lblPrompt = Label(master, text=self.prompt)
        lblPrompt.pack()

        lblHost = Label(master, text='IP/Hostname')
        self.entryHost = Entry(master)

        lblPass = Label(master, text='Password')
        self.entryPass = Entry(master, show='*')

        lblHost.pack()
        self.entryHost.pack()
        lblPass.pack()
        self.entryPass.pack()

        return None

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent=self
            )
            return 0

        self.result = result

        return 1

    def getresult(self):
        return (
        self.entryHost.get(),
        self.entryPass.get(),
        )


def askHostUserPass(parent, title, prompt):
    d = _QueryHostUserPass(title, prompt, parent)
    return d.result

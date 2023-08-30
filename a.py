import random, re, time, string
from copy import copy as duplicate
from tkinter import *
from tkinter.messagebox import showwarning, showinfo

word_list = ['pyton', 'joǵary dárejeli kodtyń oqylýyn jáne ázirleýshiniń ónimdiligin arttyrýǵa maqsattalǵan jalpy maqsattaǵy baǵdarlamalaý tili'], \
['functcia', 'append (x) - bul...'], \
['index', 'sharshy jaqshaǵa salynǵan tizim elementiniń ornalasqan jeri men Úndeýin sıpattaıdy'], \
['matrica', 'tikburyshty kestede saqtalǵan derekter'], \
['elementter', 'tizimniń quramyna kiretin aınymaly'], \
['diapazonyn', 'range fýnksıasy sandardyn nesyn jasaıdy?'], \
['massiv', 'bir tıptegi uıashyqtar toby retinde usynylǵan derekter qurylymy'], \
['spisok', 'pyton tilindegi tizbektiń bir túri'], \
['kortej', 'ózgermeıtin tizim']

class Crossword(object):
    def __init__(self, cols, rows, empty = '*', maxloops = 2000, available_words=[]):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.maxloops = maxloops
        self.available_words = available_words
        self.randomize_word_list()
        self.current_word_list = []
        self.clear_setka()

    def clear_setka(self):
        self.setka = []
        for i in range(self.rows):
            ea_row = []
            for j in range(self.cols):
                ea_row.append(self.empty)
            self.setka.append(ea_row)

    def randomize_word_list(self): 
        prostolist = []
        for word in self.available_words:
            if isinstance(word, Word):
                prostolist.append(Word(word.word, word.clue))
            else:
                prostolist.append(Word(word[0], word[1]))
        random.shuffle(prostolist)
        prostolist.sort(key=lambda i: len(i.word), reverse=True) 
        self.available_words = prostolist

    def compute_crossword(self, time_permitted = 1.00, spins=2):
        time_permitted = float(time_permitted)

        count = 0
        copy = Crossword(self.cols, self.rows, self.empty, self.maxloops, self.available_words)

        start_full = float(time.time())
        while (float(time.time()) - start_full) < time_permitted or count == 0: 
            copy.current_word_list = []
            copy.clear_setka()
            copy.randomize_word_list()
            x = 0
            while x < spins: 
                for word in copy.available_words:
                    if word not in copy.current_word_list:
                        copy.fit_and_add(word)
                x += 1
            if len(copy.current_word_list) > len(self.current_word_list):
                self.current_word_list = copy.current_word_list
                self.setka = copy.setka
            count += 1
        return

    def suggest_coord(self, word):
        count = 0
        coordlist = []
        glc = -1
        for given_letter in word.word: 
            glc += 1
            rowc = 0
            for row in self.setka: 
                rowc += 1
                colc = 0
                for cell in row: 
                    colc += 1
                    if given_letter == cell:
                        try:  
                            if rowc - glc > 0: 
                                if ((rowc - glc) + word.length) <= self.rows: 
                                    coordlist.append([colc, rowc - glc, 1, colc + (rowc - glc), 0])
                        except: pass
                        try: 
                            if colc - glc > 0: 
                                if ((colc - glc) + word.length) <= self.cols: 
                                    coordlist.append([colc - glc, rowc, 0, rowc + (colc - glc), 0])
                        except: pass
        new_coordlist = self.sort_coordlist(coordlist, word)
        
        return new_coordlist

    def sort_coordlist(self, coordlist, word): 
        new_coordlist = []
        for coord in coordlist:
            col, row, vertical = coord[0], coord[1], coord[2]
            coord[4] = self.check_fit_score(col, row, vertical, word) 
            if coord[4]: 
                new_coordlist.append(coord)
        random.shuffle(new_coordlist) 
        new_coordlist.sort(key=lambda i: i[4], reverse=True) 
        return new_coordlist

    def fit_and_add(self, word): 
        fit = False
        count = 0
        coordlist = self.suggest_coord(word)

        while not fit and count < self.maxloops:

            if len(self.current_word_list) == 0:
                vertical, col, row = random.randrange(0, 2), 1, 1
                
                if self.check_fit_score(col, row, vertical, word): 
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)
            else:
                try: 
                    col, row, vertical = coordlist[count][0], coordlist[count][1], coordlist[count][2]
                except IndexError: return 

                if coordlist[count][4]: 
                    fit = True 
                    self.set_word(col, row, vertical, word, force=True)

            count += 1
        return

    def check_fit_score(self, col, row, vertical, word):
        if col < 1 or row < 1:
            return 0

        count, score = 1, 1 
        for letter in word.word:
            try:
                active_cell = self.get_cell(col, row)
            except IndexError:
                return 0

            if active_cell == self.empty or active_cell == letter:
                pass
            else:
                return 0

            if active_cell == letter:
                score += 1

            if vertical:
                if active_cell != letter: 
                    if not self.check_if_cell_clear(col+1, row): 
                        return 0

                    if not self.check_if_cell_clear(col-1, row): 
                        return 0

                if count == 1: 
                    if not self.check_if_cell_clear(col, row-1):
                        return 0

                if count == len(word.word): 
                    if not self.check_if_cell_clear(col, row+1): 
                        return 0
            else: 
                if active_cell != letter: 
                    if not self.check_if_cell_clear(col, row-1): 
                        return 0

                    if not self.check_if_cell_clear(col, row+1): 
                        return 0

                if count == 1: 
                    if not self.check_if_cell_clear(col-1, row):
                        return 0

                if count == len(word.word): 
                    if not self.check_if_cell_clear(col+1, row):
                        return 0

            if vertical: 
                row += 1
            else: 
                col += 1

            count += 1

        return score

    def set_word(self, col, row, vertical, word, force=False):
        if force:
            word.col = col
            word.row = row
            word.vertical = vertical
            self.current_word_list.append(word)

            for letter in word.word:
                self.set_cell(col, row, letter)
                if vertical:
                    row += 1
                else:
                    col += 1
        return

    def set_cell(self, col, row, value):
        self.setka[row-1][col-1] = value

    def get_cell(self, col, row):
        return self.setka[row-1][col-1]

    def check_if_cell_clear(self, col, row):
        try:
            cell = self.get_cell(col, row)
            if cell == self.empty: 
                return True
        except IndexError:
            pass
        return False

    def ornalasu(self): 
        outStr = ""
        for r in range(self.rows):
            for c in self.setka[r]:
                outStr += '%s ' % c
            outStr += '\n'
        return outStr

    def order_number_words(self):
        self.current_word_list.sort(key=lambda i: (i.col + i.row))
        count, icount = 1, 1
        for word in self.current_word_list:
            word.number = count
            if icount < len(self.current_word_list):
                if word.col == self.current_word_list[icount].col and word.row == self.current_word_list[icount].row:
                    pass
                else:
                    count += 1
            icount += 1

    def word_bank(self): 
        outStr = ''
        prostolist = duplicate(self.current_word_list)
        random.shuffle(prostolist)
        for word in prostolist:
            outStr += '%s\n' % word.word
        return outStr

    def surak(self,order=True): 
        OutStr = ""
        if order:
            self.order_number_words()

        copy = self

        for word in self.current_word_list:
            copy.set_cell(word.col, word.row, word.number)

        for r in range(copy.rows):
            for c in copy.setka[r]:
                OutStr += '%s ' % c
            OutStr += '\n'

        OutStr = re.sub(r'[a-z]', ' ', OutStr)
        
        outStr = ''
        for word in self.current_word_list:
            outStr += '%d. %s: %s\n' % (word.number, word.down_across(), word.clue )

        return outStr

class Word(object):
    def __init__(self, word=None, clue=None):
        self.word = re.sub(r'\s', '', word.lower())
        self.clue = clue
        self.length = len(self.word)
   
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None

    def down_across(self): 
        if self.vertical: 
            return 'ustiden astyga'
        else: 
            return 'sol jaktan onga'

        def __repr__(self):
            return self.word

a = Crossword(15,15, '*', 5000, word_list)
a.compute_crossword(2)
print ('Koldanylgan sozder:\n',a.word_bank(),sep="")
print (a.ornalasu())
print (a.surak())
print ('Barlygy',len(word_list),'sozden',len(a.current_word_list),'soz sozjumbakta koldanyldy')

class CellEntry(Entry):
    def __init__(self, master, **kw):
        self._variable = StringVar()
        super().__init__(master, textvariable=self._variable, **kw)
  
class App:
    def __init__(self, crossword):
        self.root = Tk()
        self.root.title("Sozjumbak")
        self.root.geometry("+400+200")
        self._crossword = crossword
        self._setka = Frame(self.root)
        self._setka.pack(padx=10, pady=10)
        self._cells = {}
        #кросвордтын әрбір әрпін новый entry-га енгізу 
        for col in range(1, crossword.cols + 1):
            for row in range(crossword.rows):
                c = crossword.get_cell(col, row)
                if c != '*':
                    entry = CellEntry(self._setka, width=2, justify=CENTER)
                    entry.grid(row=row, column=col)
                    self._cells[(col, row)] = entry
        # әрбір баған мен жолға сәйкес индекс қою
        for w in crossword.current_word_list:
            row, col = w.row, w.col
            if w.down_across() == 'ustiden astyga':
                row -= 1
            else:
                col -= 1
            Label(self._setka, text=str(w.number)).grid(column=col, row=row)

        Button(self.root, text='Tekseru', command=self.check).pack(pady=10)
        Label(self.root, text=a.surak(),justify=LEFT).pack()
        
    def check(self):
        for (col, row), entry in self._cells.items():
            a=entry.get()

        entry.get().split().sort()
        self._crossword.get_cell(col, row).sort()

        if len(entry.get())==0:
            showwarning('Jauaby', 'Sozjumbakty tolyk toltyru kerek')
        elif entry.get() != self._crossword.get_cell(col, row):
            showwarning('Jauaby', 'Siz katelik jasadynyz')
        else:    
            showinfo('Jauaby', 'Barlygy dyrys.Kuttuktaimyn!!!')

    def run(self):
        self.root.mainloop()

App(a).run()
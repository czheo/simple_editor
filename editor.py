import sys
import curses

class Editor:
    def __init__(self, win, file_name):
        self.win = win
        self.file_name = file_name
        self.cur_x, self.cur_y = 0, 0 # cursor position
        self.win_x, self.win_y = 0, 0 # window top left position
        self.bar_msg = f'{self.cur_x}, {self.cur_y}'
        self.read_file()
    
    def read_file(self):
        with open(self.file_name, 'a+') as f:
            f.seek(0)
            self.buff = f.readlines()
            if not self.buff:
                self.buff.append('\n')

    def write_file(self):
        with open(self.file_name, 'w') as f:
            for line in self.buff:
                f.write(line)

    def draw(self):
        def show_bar():
            msg = self.bar_msg[:self.win_w-1]
            self.win.addstr(self.win_h - 1, 0, msg)

        def show_text():
            for i in range(self.win_x, min(len(self.buff), self.win_x + self.win_h - 1)):
                line = self.buff[i]
                line = line[self.win_y : self.win_y + self.win_w]
                self.win.addstr(line if line else '\n')

        def update_cursor_position():
            self.win.move(self.cur_x - self.win_x, self.cur_y - self.win_y)

        def update_window_position():
            self.win_h, self.win_w = self.win.getmaxyx() # window height, width
            if self.cur_x < self.win_x:
                self.win_x = self.cur_x
            if self.cur_y < self.win_y:
                self.win_y = self.cur_y
            if self.cur_x > self.win_x + self.win_h - 2:
                self.win_x = self.cur_x - self.win_h + 2
            if self.cur_y > self.win_x + self.win_w- 2:
                self.win_y = self.cur_y - self.win_w + 2
        self.win.clear()
        update_window_position()
        show_text()
        show_bar()
        update_cursor_position()
   
    def read_key(self):
        def move_up():
            self.cur_x = max(self.cur_x - 1, 0)
            self.cur_y = min(self.cur_y, len(self.buff[self.cur_x]) - 1)

        def move_down():
            self.cur_x = min(self.cur_x + 1, len(self.buff) - 1)
            self.cur_y = min(self.cur_y, len(self.buff[self.cur_x]) - 1)

        def move_left():
            self.cur_y = max(self.cur_y - 1, 0)

        def move_right():
            self.cur_y = min(self.cur_y + 1, len(self.buff[self.cur_x]) - 1)

        def insert_ch(c):
            line = self.buff[self.cur_x]
            self.buff[self.cur_x] = line[:self.cur_y] + c + line[self.cur_y:]
            self.cur_y += 1

        def delete():
            if self.cur_y == 0: # at the start of line
                if self.cur_x != 0: # not first line
                    prev_line = self.buff[self.cur_x - 1]
                    self.buff[self.cur_x - 1] = prev_line[:-1] + self.buff[self.cur_x]
                    self.buff.pop(self.cur_x)
                    self.cur_x -= 1
                    self.cur_y = len(prev_line) - 1
            else:
                line = self.buff[self.cur_x]
                self.buff[self.cur_x] = line[:self.cur_y-1] + line[self.cur_y:]
                self.cur_y -= 1
        
        def new_line():
            line = self.buff[self.cur_x]
            self.buff[self.cur_x] = line[:self.cur_y] + '\n'
            self.buff.insert(self.cur_x + 1, line[self.cur_y:])
            self.cur_x += 1
            self.cur_y = 0

        key = self.win.getch()
        if key == curses.KEY_UP:
            move_up()
        elif key == curses.KEY_DOWN:
            move_down()
        elif key == curses.KEY_LEFT:
            move_left()
        elif key == curses.KEY_RIGHT:
            move_right()
        elif key == 24: # ctrl-x
            self.write_file()
            self.bar_msg = f'saved to {self.file_name}'
        elif key == 9:  # tab
            for i in range(4):
                insert_ch(' ')
        elif key == 10: # new line
            new_line()
        elif key == 127: # delete
            delete()
        elif 0 <= key < 128:
            insert_ch(chr(key))

    def run(self):
        self.draw()
        while True:
            self.bar_msg = f'{self.cur_x}, {self.cur_y}'
            self.read_key()
            self.draw()

def main(win):
    editor = Editor(win, sys.argv[1])
    editor.run()

curses.wrapper(main)

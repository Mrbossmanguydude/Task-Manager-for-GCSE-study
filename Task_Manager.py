import pygame
import os
import datetime
import pickle

pygame.init()

#Initialising Constants 

WIDTH, HEIGHT = 1000, 500
FPS = 60
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
WEEKDAYS = ["Monday", "Tuesday", "Thursday", "Friday"]
INTERVENTIONS = ["Wednesday"]
WEEKENDS = ["Saturday", "Sunday"]
MAX_TICKS = 8


'''
Default timetable below, notation:
(t-24hrtime-Activity--)n 
n = number of tasks in day
t = time identifier
--, - =  regular spaces to differentiate tasks
'''
TIMETABLE = {
    "Weekend": "t-0900-Get up, have breakfast.--t-1100-Study time.--t-1500-Start playing.--t-1600-Study again.--t-1800-Code.--t-2000-Study again.--t-2100-Have dinner.--t-2300-Sleep.",
    "Weekday": "t-0630-Wake up for school.--t-1500-lunch/games.--t-1600-Start to code/HW.--t-1800-Start study.--t-2100-Have dinner.--t-2300-Sleep.",
    "Intervention": "t-0630-Wake up for school.--t-1630-lunch/games.--t-1730-Start to code/HW.--t-1830-Start study.--t-2100-Have dinner.--t-2300-Sleep."
} 

FONT = "fonts\\pixel_font-1.ttf" #Custom pixel Font in Fonts directory.
SUBJECTS = ["Physics", "Maths", "Eng Lit", "Eng Lang", "Geography", "Biology", "Chemistry", "Spanish", "FMaths", "Computing"]

#Functions to convert between 12&24hr time.
time_convert_12 = lambda time: str(int(time[:-3]) - 12)+":"+time[-2:]+"pm" if int(time[:-3]) > 12 else time+"am" if int(time[:-3]) < 12 else time+"pm" if int(time[:-3]) == 12 else "12 "+time[-3:]+"am" if int(time[:-3]) == 0 else time+"pm"
time_convert_24 = lambda time: str(int(time[:-5]) + 12 if "pm" in time else int(time[:-5])) + time[-5:-2] if int(time[:-5]) != 12 else "00" + time[-5:-2] if "am" in time else time[:-2]

class Button:
    '''
    Holds the information and interactable Rect for an operational button. 

    Attributes:
    rect (pygame.Rect): The pygame rectangle that is interacted with. Also stores coordinates and lengths.
    text (str): The string of text that entails the prompt of the button.
    text_size (int): Determines the size of text in box.
    textcolor (tuple): The color of displayed text, stored as (r, g, b) values.
    bordercolor (tuple): The color of the surrounding button outline, stored as (r, g, b) values.
    thickness (int): How wide the outline of the rect is.
    clicked_ticks (int): Stores iterations or 'ticks' passed since last click.
    clicked (bool): Information for whether the button has been clicked or not.
    
    '''
    def __init__(self, x, y, width, height, text, text_size, bordercolor=(0, 0, 0), textcolor=(0, 0, 0), thickness=5):
        '''
        Initialises the Button with its text, color, size and coordinates.

        Parameters:
        x (int): Specified x coordinate of the topleft of the rect.
        y (int): Specified y coordinate of the topleft of the rect.
        width (int): Amount of pixels specifying the width of the Rect.
        height (int): Amount of pixels specifying the height of the Rect.
        text (str): The string of text that entails the prompt of the button.
        text_size (int): Determines the size of text in box.
        textcolor (tuple): The color of displayed text, stored as (r, g, b) values.
        bordercolor (tuple): The color of the surrounding button outline, stored as (r, g, b) values.
        thickness (int): How wide the outline of the rect is.

        '''
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.topleft = (x, y)
        self.text = text
        self.text_size = text_size
        self.textcolor = textcolor
        self.bordercolor = bordercolor
        self.thickness = thickness
        self.clicked_ticks = 0
        self.clicked = False

    def get_clicked(self):
        #Check for a left mouse button click.
        if self.clicked_ticks >= FPS:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]: #Index 0 specifies left mouse button.
                    self.clicked = True #Button is clicked if a collision with mouse and Rect is detected.
        else:
            self.clicked = False #Otherwise, the button is not clicked.

    def draw(self):
        #Draws out the button and its border.
        draw_highlighted_rect(screen, self.rect, self.bordercolor, self.bordercolor, self.thickness, self.thickness)
        draw_text(screen, FONT, self.text, (self.rect.x + 15, self.rect.y), self.text_size, self.textcolor)

class Menu:
    '''
    Class that stores the state of variables in the Menu screen specifically. This includes the tick sheet per subject
    as well as the current and future activities specified by the timetable.

    Attributes:
    now_rect (pygame.Rect): Used to specify the border of the task happening now in the timetable.
    next_rect (pygame.Rect): Used to specify the border of the task happening next in the timetable.
    date_today (str): Stores the current day's information in YYYY-MM-DD format.
    now_text (str): The current task in the timetable.
    next_text (str): The next task in the timetable.
    time (str): The time of the next task.

    '''
    def __init__(self):
        self.now_rect = pygame.Rect(0, HEIGHT - 70, 500, 70)
        self.next_rect = pygame.Rect(0, 365, 500, 70)
        time = str(datetime.datetime.now())[11:16] # Specifies time in 24hr format (current time).
        day = DAYS[datetime.datetime.now().weekday()] # The current day (eg: Monday, Tuesday, etc)
        self.date_today = str(datetime.datetime.now())[:10] 

        day_type = "Intervention" if day in INTERVENTIONS else "Weekend" if day in WEEKENDS else "Weekday"
        self.now_text = self.update_now(TIMETABLE[day_type], time)[0]
        self.next_text = self.update_now(TIMETABLE[day_type], time)[1]
        self.time = self.update_now(TIMETABLE[day_type], time)[2]

    def update_now(self, timetable : str, time : str) -> tuple:
        '''
        Function that calculates the current, next and time for next tasks based on the current time and given timetable.

        Parameters:
        timetable (str): The timetable using specified notation previously set.
        time (str): The 24hr current time.

        Returns:
        tuple : Current task, Next task, Time of next task
        '''
        tasks = timetable.split("--")
        int_time = int(time[:2] + time[3:])
        for task in range(len(tasks)):
            if int(tasks[task][2:6]) > int_time:
                return tasks[task-1][7:], tasks[task][7:], int(tasks[task][2:6]) #Current task of timetable.
        return "sleeping", "sleeping", "1100PM+" #If current time doesnt fall in range of timetable, I have to be sleeping.

    def draw(self):
        #Draws out the Menu screen.
        pygame.draw.line(screen, (0, 0, 0), ((WIDTH//2) - 5, 0), ((WIDTH//2) - 5, HEIGHT), 10)
        draw_text(screen, FONT, "MENU", ((WIDTH//2) - 175, 0), 75, (100, 100, 100))
        draw_highlighted_rect(screen, self.now_rect, (0, 0, 0), (0, 0, 0), 5, 5)
        draw_highlighted_rect(screen, self.next_rect, (0, 0, 0), (0, 0, 0), 5, 5)
        draw_text(screen, FONT, f"NOW - {self.now_text}", (self.now_rect.x + 20, self. now_rect.y + 10), 40, (0, 0 ,0))
        draw_text(screen, FONT, self.date_today, (20, 20), 40, (100, 100, 100))
        draw_text(screen, FONT, f"NEXT@{str(self.time)[:2]}:{str(self.time)[2:]} - {self.next_text}", (15, 370), 40, (0, 0 ,0))

class Calendar:
    '''
    Class that stores the state of variables in the Calendar screen specifically. This includes the day screen, as well as 
    all the days and months in 2024 with editable task boxes for each day.

    Attributes:
    day (int): The current day's number relative to the month it is in.
    current_month (int): The current month's number out of 12. (eg: June -> 6)
    month_lengths (dict): A dictionary comprising of all the months and their lengths in terms of days in 2024.
    month_data (dict): Stores the initialised empty string values for each day's task box in 2024.
    day_window (bool): True, if any day's task list is opened (also known as the day window).
    selected_day (int): Initialised to None, but once day is clicked, that day number is set as 'selected_day' based on index in the month_data dict.
    selected_task (int): Initialised to None, but once a task is selected in that day, it corresponds to that paticular index in the month_data dict.
    day_rects (dict): A list of rects which comprise the day boxes in the Calendar screen as values and the month as key.
    task_rects (dict): A dict of rects which comprise the task boxes in the day window.

    '''
    def __init__(self): 
        #Initialises all variables pertaining to day_window and Calendar scereen.

        self.day = datetime.datetime.today().day
        self.current_month = datetime.datetime.today().month
        self.current_day_name = datetime.date.today().strftime("%A")
        
        self.month_lengths = {
            "January": 31,
            "February": 29,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31
        }
        self.month_data = {}
        for month, days in self.month_lengths.items():
            self.month_data[month] = [["", "", "", "", "", ""] for _ in range(days)]
            '''
            This dict is multidimensional, the order of items goes in the order below, 
            where n() shows a repeat in that structure:

            self.month_data = { n(Month_name : [n(["", "", "", "", "", ""])]) }

            To summarise, each month in 2024, has a list (all the days, where each sub list is a day) 
            of lists (which hold the data for each task box as a string), to allow data from the 
            .pickle file to be loaded onto the month_data dict.
            ''' 
        self.day_window = False
        self.selected_day = None
        self.selected_task = None

        self.day_rects = {}
        self.task_rects = {}

        positions = []
        width = 100
        height = 100

        #Loop organises the positions of all rects present on the Calendar screen for each month and each day in that month, beforehand.
        for month in self.month_data:
            self.day_rects[month] = []
            self.task_rects[month] = []
            current_pos = [-width, 100]
            for day in self.month_data[month]:
                taskbox_pos = [0, 70]
                if current_pos[0] + width*2 > WIDTH:
                    current_pos[0] = 0
                    current_pos[1] += height
                else:
                    current_pos[0] += width

                #Seperate loop to organise the task boxes in each day of each month.
                for _ in day:
                    self.task_rects[month].append(pygame.Rect(*taskbox_pos, WIDTH, 70))
                    taskbox_pos[1] += 70
                positions.append(tuple(current_pos))
                self.task_rects
                self.day_rects[month].append(pygame.Rect(*current_pos, width, height))

    def day_name(self, month : int, day : int) -> str:
        #Returns the paticular day name based on a given day and month (in 2024).
        target_date = datetime.datetime(2024, month, day)
        day_name = target_date.strftime("%A")
        return day_name

    def draw(self):
        #Draws all the rects and lines for the Calendar screen or day window depending on self.day_window.
        if not self.day_window:
            #If Calendar screen
            draw_text(screen, FONT, str(MONTHS[self.current_month - 1]), (10, 0), 65, (100, 100, 100))
            num = 1
            day_index = 1
            for rect in self.day_rects[MONTHS[self.current_month - 1]]:
                color = (255, 0, 0) if datetime.datetime.today().day == num and datetime.datetime.now().strftime("%B") == MONTHS[self.current_month - 1] else (0, 0, 0)
                draw_highlighted_rect(screen, rect, color, color, 1, 1)
                draw_text(screen, FONT, f"{str(num)} {self.day_name(self.current_month, day_index)[0]}", (rect.x + 4, rect.y - 5), 45, (255, 0, 0))
                num += 1
                day_index += 1

        else:
            #Otherwise day_window
            draw_text(screen, FONT, f"{str(MONTHS[self.current_month - 1])} {str(self.selected_day + 1)}", (10, 0), 65, (100, 100, 100))
            current_pos = [0, 70]
            for task in self.month_data[MONTHS[self.current_month - 1]][self.selected_day]:
                pygame.draw.line(screen, (0, 0, 0), current_pos, (WIDTH, current_pos[1]), 5)
                draw_text(screen, FONT, task, current_pos, HEIGHT//6, (55, 68, 100))
                current_pos[1] += 70
class Tasks:
    '''
    Class that stores the state of variables in the Task screen specifically. This only includes tasks and notes on them (extra info).

    Attributes:
    task_boxes (list): List of Rects that comprise the task boxes.
    notes_boxes (list): List of Rects that comprise the notes boxes.
    tasks (list): List of strings with corresponding indexes to its Rect list that stores the actual tasks as strings.
    notes (list): List of strings with corresponding indexes to its Rect list that stores the actual notes as strings.
    '''
    def __init__(self, max_tasks : int):
        '''
        Initialises the positions of rects and empty strings of all the task and note boxes.

        Parameters:
        max_tasks (int): The max number of tasks projected on the screen (along with its corresponding note box).
        '''
        self.task_boxes = [pygame.Rect(0, i*HEIGHT//max_tasks + HEIGHT//max_tasks, WIDTH//3, HEIGHT//max_tasks) for i in range(max_tasks - 1)]
        self.notes_boxes = [pygame.Rect(WIDTH//3, j*HEIGHT//max_tasks + HEIGHT//max_tasks, WIDTH - WIDTH//3, HEIGHT//max_tasks) for j in range(max_tasks - 1)]
        self.tasks = ["" for _ in range(max_tasks)]
        self.notes = ["" for _ in range(max_tasks)]

    def check_mouseclick(self) -> tuple:
        '''
        This method calculates the mouse's state and position.

        Returns:
        clicked (bool): Whether or not the mosue clicked something.
        notes_or_tasks (str): Whether notes or task boxes were clicked.
        index (int): Index in either task or note boxes list depending specifically on which one was chosen.
        '''
        mouse_pos = pygame.mouse.get_pos()
        notes_or_tasks = ""
        index = None #Will hold value of index of either one of task or note boxes list.
        clicked = False
        for rect in self.task_boxes: #Loops through task boxes to check for collisions with mouse.
            if rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]: #Checks for left click.
                    clicked = True
                    index = self.task_boxes.index(rect) #Accordingly logs the correct index in task_boxes list (marked as selected).

                elif pygame.mouse.get_pressed()[2]: #Checks for right click.
                    clicked = True
                    index = self.task_boxes.index(rect)

                    self.tasks[index] = "" #Clears that paticular boxes text (a delete function to delete all at once).

                notes_or_tasks = "tasks" 

        for rect in self.notes_boxes: #Loops through notes boxes to check for collisions with mouse.
            if rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]: #Checks for left click.
                    clicked = True
                    index = self.notes_boxes.index(rect) #Accordingly logs the correct index in notes_boxes list (marked as selected).

                elif pygame.mouse.get_pressed()[2]: #Checks for right click.
                    clicked = True
                    index = self.notes_boxes.index(rect)

                    self.notes[index] = "" #Clears that paticular boxes text (a delete function to delete all at once).

                notes_or_tasks = "notes"
        return (clicked, notes_or_tasks, index)

    def draw(self):
        #Draws all the rects and lines for the Tasks screen.
        draw_text(screen, FONT, "TASKS", (5, -5), 75, (100, 100, 100))
        draw_text(screen, FONT, "NOTES", (WIDTH//3 + 5, -5), 75, (100, 100, 100))
        pygame.draw.line(screen, (0, 0, 0), (WIDTH//3, 0), (WIDTH//3, HEIGHT), 3)

        #Loops to procedurally draw task and note boxes.
        for task in self.task_boxes:
            draw_highlighted_rect(screen, task, (0, 0, 0), (0, 0, 0), 1, 1)
            draw_text(screen, FONT, self.tasks[self.task_boxes.index(task)], (task.x + 5, task.y), task.height, (200, 50, 50))
        for note in self.notes_boxes:
            draw_highlighted_rect(screen, note, (0, 0, 0), (0, 0, 0), 1, 1)
            draw_text(screen, FONT, self.notes[self.notes_boxes.index(note)], (note.x + 5, note.y), note.height, (50, 250, 50))

class Check_list:
    '''
    Holds the information for the checklist seen on the Menu screen, this obj interacts with the actual .pickle file
    to store and save accurately, how many ticks were logged for each subject.

    Attributes:
    checks (list): Initialised to 0s, a 'counter' list for all ticks for each subject where each subject corresponds to an index (hence, range(len(SUBJECTS))).
    tick_img (pygame.Surface): An image of a tick, stored as a pygame surface.
    tick_marks (dict): Indexes for each key correspond with the checks list. Each key is the subject while each value is the amount of ticks attributed to that subject.
    box_rects (list) : A list of all the rects for each subject's task box.
    '''
    def __init__(self, tick_img : pygame.surface.Surface):
        '''
        Initialises all empty (to be updated) check counters and tick mark lists and dict. 

        Parameter:
        tick_img (pygame.Surface): A valid surface image of a tick.
        '''
        self.checks = [0 for _ in range(len(SUBJECTS))] #Note: This is technically redundant, as tick_marks stores these values nevertheless, but reduces complexity when displaying.
        self.tick_img = tick_img
        self.tick_marks = {}
        for i in range(len(SUBJECTS)):
            self.tick_marks[SUBJECTS[i]] = self.checks[i]
        self.box_rects = [pygame.Rect(WIDTH//2, i*50, WIDTH//2, HEIGHT//len(SUBJECTS)) for i in range(len(SUBJECTS))]

    def draw(self):
        #Draws all the rects and lines for the Checklist.

        #Loop to iterate through the tick box rects for each subject.
        for i, box in enumerate(self.box_rects):
            draw_highlighted_rect(screen, box, (0, 0, 0), (0, 0, 0), 1, 1)
            draw_text(screen, FONT, SUBJECTS[i], (WIDTH//2 + 5, i*50), 20, (255, 255, 255))
            pygame.draw.line(screen, (0, 0, 0), (WIDTH//2 + 100, 0), (WIDTH//2 + 100, HEIGHT), 3)

        #Loop to iterate through the actual tick marks dict and blit the correct amount of tick_imgs procedurally.
        for i, subject in enumerate(self.tick_marks):
            for j in range(self.tick_marks[subject]):
                screen.blit(self.tick_img, ((WIDTH//2 + 100) + 50*j, 50*i))

def draw_highlighted_rect(surface : pygame.surface.Surface, rect : pygame.rect.Rect, border_color : tuple, highlight_color : tuple, border_thickness : int, highlight_thickness : int):
    '''
    This Function, given a screen surface and a rect, 'highlights' a border around that rect and draws it to the given surface.

    Parameters:
    surface (pygame.Surface): Typically the 'screen' that the rect is meant to be drawn on.
    rect (pygame.Rect): The actual Rect being blit.
    border_color (tuple): The color of the border.
    highlight_color (tuple): The color of the highlight of the border.
    border_thickness (int): A measure how many pixels wide or 'thick' the border is meant to be.
    highlight_thickness (int): A measure how many pixels wide or 'thick' the highlight of the border is meant to be.
    '''
    pygame.draw.rect(surface, border_color, rect, border_thickness)
    inner_rect = pygame.Rect(rect.left + border_thickness, rect.top + border_thickness,rect.width - 2 * border_thickness, rect.height - 2 * border_thickness)
    pygame.draw.rect(surface, highlight_color, inner_rect, highlight_thickness)

def draw_text(surface : pygame.surface.Surface, font : pygame.font.Font, text : str, pos : tuple, fontsize : int, color : tuple):
    '''
    Given information on text and font, this function draws a string of text as a pygame surface.

    Parameters:
    surface (pygame.Surface): Typically the 'screen' that the rect is meant to be drawn on.
    font (str): A file path of the font file used.
    text (str): The string of text that is to be drawn.
    pos (tuple): The position of the start of the text as (x, y) values.
    fontsize (int): Measure of how big the font should be drawn.
    color (tuple): color of words displayed.
    '''
    font = pygame.font.Font(font, fontsize) # Font is reassigned as a pygame.Font obj to be blit.
    word = font.render(text, True, color)
    surface.blit(word, (pos[0], pos[1])) #word blit at right position in given font.

def today(calendar):
    '''
    Function to draw the today screen, given information from the calendar obj. Acts as a slight shortcut for the calendar.

    Parameters:
    calendar (Calendar): The Calendar class holds the information to draw any day_window such as this one.
    '''

    #The same as day_window's blit (as it is essentially just the same screen, just for today).
    calendar.selected_day = calendar.day - 1
    draw_text(screen, FONT, f"{str(MONTHS[calendar.current_month - 1])} {str(calendar.selected_day + 1)}", (10, 0), 65, (100, 100, 100))
    current_pos = [0, 70]
    for task in calendar.month_data[MONTHS[calendar.current_month - 1]][calendar.selected_day]:
        pygame.draw.line(screen, (0, 0, 0), current_pos, (WIDTH, current_pos[1]), 5)
        draw_text(screen, FONT, task, current_pos, HEIGHT//6, (55, 68, 100))
        current_pos[1] += 70

def reset_buttons(buttons : list):
    '''
    Resets all button's ticks to zero, and sets them as 'not clicked'.

    Parameter:
    buttons (list): List of all buttons as Button objs.
    '''
    for button in buttons:
        button.clicked_ticks = 0
        button.clicked = False

def increment_button_ticks(buttons : list):
    '''
    Increments all button's ticks by one, as long they havent been clicked for a second.

    Parameter:
    buttons (list): List of all buttons as Button objs.
    '''

    for button in buttons:
        if button.clicked_ticks < FPS: #Uses FPS to ensure only close to a second is there for button delay.
            button.clicked_ticks += 1

def split_list(input_list, chunk_size):
    '''
    Splits a list in chunk_size parts.

    Parameters:
    input_list (list): The given list of items.
    chunk_size (int): A size of the chunks of the list.

    Returns:
    A 2 dimensional list, where each 'chunk' is a sub list, comprising of chunk_size parts of input_list in order
    of original list. If chunk_size >= len(input_list), then a list of the original list is returned.Negative  
    chunk sizes return an empty list.
    '''
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def load_data():
    #Loads data from the data.pickle file and returns it.
    try:
        with open('data.pickle', 'rb') as f:
            data = pickle.load(f)
            return data
    except EOFError: 
        return "" # For a potential error an empty string is returned.
    
def clear_savedata():
    #Clears all data from data.pickle. WARNING : BE CAREFUL OF USE, THIS DELETES ALL THE CONTENTS OF THE FILE.
    with open("data.pickle", "wb") as _:
        pass

def save(objects, tasks, calendar):
    '''
    Saves all data needed (this is specified beforehand and is constant).

    Parameters:
    objects (dict): dict of some objects that use string names to easily refer to the objs themselves.
    tasks (Tasks): The Tasks obj.
    calendar (Calendar): The Calendar obj.
    '''
    with open("data.pickle", "wb") as f:
        #Previously set, recorded data.
        data = {
            "checks": objects["check_list"].checks, 
            "tick_marks": objects["check_list"].tick_marks,
            "tasks": tasks.tasks,
            "notes": tasks.notes,
            "month_data": calendar.month_data
        }
        pickle.dump(data, f) #Puts the data dict in the pickle file.
    f.close() #Close the file.

def main(screen):
    '''
    This Function corroborates all classes, methods and other functions into one main pygame loop.
    Along with most of the main definitions of variables.

    Parameter:
    screen (pygame.Surface): The main screen everything will be blit on.
    '''

    #Definition of all main objs.
    tasks = Tasks(10)
    checklist = Check_list(pygame.image.load(os.path.join("images", "tick_mark.png")))
    calendar = Calendar()
    menu = Menu()

    #loads data from data.pickle, if it exists and isnt empty.
    if os.path.exists("data.pickle"):
        data = load_data()
        if data != "":
            data = load_data()
            checklist.checks = data["checks"]
            checklist.tick_marks = data["tick_marks"]
            tasks.tasks = data["tasks"]
            tasks.notes = data["notes"]
            calendar.month_data = data["month_data"]

    #Definition of all buttons.
    calendar_button = Button(175, 295, 325, 75, "Calendar", 75, textcolor=(100, 100, 100), bordercolor=(0, 0, 0))
    today_button = Button(175, 230, 325, 75, "Today", 75, textcolor=(100, 100, 100), bordercolor=(0, 0, 0))
    tasks_button = Button(175, 165, 325, 75, "Tasks", 75, textcolor=(100, 100, 100), bordercolor=(0, 0, 0))
    calendar_back_button = Button(WIDTH - 125, 0, 125, HEIGHT//10, "Back", 50, textcolor=(100, 0, 0), bordercolor=(0, 0, 0), thickness=3)
    tasks_back_button = Button(WIDTH - 125, 0, 125, HEIGHT//10, "Back", 50, textcolor=(100, 0, 0), bordercolor=(0, 0, 0), thickness=3)
    today_back_button = Button(WIDTH - 125, 0, 125, HEIGHT//10, "Back", 50, textcolor=(100, 0, 0), bordercolor=(0, 0, 0), thickness=3)
    day_window_back_button = Button(WIDTH - 125, 0, 125, HEIGHT//10, "Back", 50, textcolor=(100, 0, 0), bordercolor=(0, 0, 0), thickness=3)

    #Definition of some important lists of buttons and other objs.
    menu_buttons = [calendar_button, today_button, tasks_button]
    objects = {"menu": menu, "check_list": checklist}
    buttons = [calendar_button, today_button, tasks_button, calendar_back_button, tasks_back_button, today_back_button, day_window_back_button]

    #Initial set states.
    current_state = "menu"
    editing = False
    editing_index = None
    editing_list = None

    #Pygame clock to record framerate.
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FPS) #Framerate is managed.
        increment_button_ticks(buttons) #All button's ticks incremneted at the start of the loop.
        pygame.display.set_caption(f"Task Manager - {str(int(clock.get_fps()))}") #Updates caption based on framerate.
        screen.fill((50, 50, 50)) #Background of the screen.

        #Event check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                save(objects, tasks, calendar)

            #For the main menu
            if current_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        #Updates now_rect, next_rect and time based on a left mouse click on the now_rect.
                        if objects["menu"].now_rect.collidepoint(event.pos):
                            time = str(datetime.datetime.now())[11:16]
                            day = DAYS[datetime.datetime.now().weekday()]
                            day_type = "Weekday" if day in WEEKDAYS else "Weekend" if day in WEEKENDS else "Intervention"
                            objects["menu"].now_text = objects["menu"].update_now(TIMETABLE[day_type], time)[0]
                            objects["menu"].next_text = objects["menu"].update_now(TIMETABLE[day_type], time)[1]
                            objects["menu"].time = objects["menu"].update_now(TIMETABLE[day_type], time)[2]
                            
                        else:
                            #Otherwise look for collisions in the check_list.
                            for i, box in enumerate(objects["check_list"].box_rects):
                                if box.collidepoint(event.pos):
                                    if objects["check_list"].tick_marks[SUBJECTS[i]] <= 7:
                                        objects["check_list"].tick_marks[SUBJECTS[i]] += 1 #increments a tick as long as it is <= 7.

                        #Checks for clicks on the menu buttons and updates the state accordingly.
                        #Note : This can be done more efficiently through simple iteration but the foreseen addition of an attribute may complicate things.
                        for button in menu_buttons:
                            button.get_clicked()
                        if menu_buttons[2].clicked:
                            current_state = "tasks"

                        elif menu_buttons[1].clicked:
                            current_state = "today"

                        elif menu_buttons[0].clicked:
                            current_state = "calendar"

                    #Otherwise checks for right clicks on the check_list rects and decrements it by one if detected.
                    elif event.button == 3:
                        for i, box in enumerate(objects["check_list"].box_rects):
                                if box.collidepoint(event.pos):
                                    if objects["check_list"].tick_marks[SUBJECTS[i]] > 0:
                                        objects["check_list"].tick_marks[SUBJECTS[i]] -= 1
            #For the tasks screen.
            elif current_state == "tasks":

                #Back button check.
                tasks_back_button.get_clicked()
                if tasks_back_button.clicked and not editing:
                    current_state = "menu"
                    reset_buttons(buttons)

                #Based on checked mouseclick, 'boxes_info' is updated as to select a paticular note or task box.    
                boxes_info = tasks.check_mouseclick()

                if boxes_info[0]:
                    editing = True
                    if boxes_info[1] == "notes":
                        editing_index = boxes_info[2]
                        editing_list = tasks.notes
                        editing_notesortasks = "notes"
                    elif boxes_info[1] == "tasks":
                        editing_index = boxes_info[2]
                        editing_list = tasks.tasks
                        editing_notesortasks = "tasks"

                #Typing events when editing the interactable text boxes (essentially the same as calendar's checks below).
                elif event.type == pygame.KEYDOWN and editing:
                    if event.key == pygame.K_ESCAPE:
                        editing = False
                        editing_index = None
                        editing_list = None
                    
                    else:
                        if event.key == pygame.K_BACKSPACE:
                            editing_list[editing_index] = editing_list[editing_index][:-1]
                        else:
                            editing_list[editing_index] += event.unicode

                        if editing_notesortasks == "notes":
                            tasks.notes = editing_list
                        else:
                            tasks.tasks = editing_list

            #For the calendar scereen.
            elif current_state == "calendar":

                #Back button check.
                calendar_back_button.get_clicked()
                day_window_back_button.get_clicked()
                if calendar_back_button.clicked and not calendar.day_window:
                    current_state = "menu"
                    reset_buttons(buttons)

                elif day_window_back_button.clicked and calendar.day_window and not editing:
                    calendar.selected_day = None
                    calendar.day_window = False
                    current_state = "calendar"
                    reset_buttons(buttons)

                #Typing events when editing the interactable text boxes.
                elif event.type == pygame.KEYDOWN and editing:
                    if event.key == pygame.K_ESCAPE:
                        editing = False
                    else:
                        if event.key == pygame.K_BACKSPACE:
                            #Removes the last piece of text if backspace is clicked.
                            calendar.month_data[MONTHS[calendar.current_month - 1]][calendar.selected_day][calendar.selected_task] = calendar.month_data[MONTHS[calendar.current_month - 1]][calendar.selected_day][calendar.selected_task][:-1]
                        else:
                            #Otherwise, for any other letter, it is added on to the string at the specified selected indexes in month data.
                            calendar.month_data[MONTHS[calendar.current_month - 1]][calendar.selected_day][calendar.selected_task] += event.unicode

                #To traverse the months of 2024 based on arrow keys.            
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if calendar.current_month > 1:
                            calendar.current_month -= 1  

                    elif event.key == pygame.K_RIGHT:
                        if calendar.current_month < 12:
                            calendar.current_month += 1

                #Checks for mouse collisions with the task rect and sets selected indexes accordingly.
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not calendar.day_window:
                            for day_rect in calendar.day_rects[MONTHS[calendar.current_month - 1]]:
                                if day_rect.collidepoint(event.pos):
                                    index = calendar.day_rects[MONTHS[calendar.current_month - 1]].index(day_rect)
                                    calendar.selected_day = index
                                    calendar.day_window = True

                        else:
                            for task_rect in split_list(calendar.task_rects[MONTHS[calendar.current_month - 1]], 6)[calendar.selected_day]:
                                if task_rect.collidepoint(event.pos):
                                    index = split_list(calendar.task_rects[MONTHS[calendar.current_month - 1]], 6)[calendar.selected_day].index(task_rect)
                                    calendar.selected_task = index
                                    editing = True
            
            #For the today screen.
            elif current_state == "today":

                #Back button check. 
                today_back_button.get_clicked()
                if today_back_button.clicked:
                    calendar.selected_day = None
                    current_state = "menu"
                    reset_buttons(buttons)

        #Draws a specific back button based on current state (to know which state to switch to if needed).
        if current_state == "today":
            today(calendar)
            today_back_button.draw()
                        
        if current_state == "calendar":
            calendar.draw()
            if calendar.day_window:
                day_window_back_button.draw()

            else:
                calendar_back_button.draw()

        if current_state == "menu":
            for obj in objects.values():
                obj.draw()
            for button in menu_buttons:
                button.draw()

        elif current_state == "tasks":
            tasks.draw()
            tasks_back_button.draw()

        #A red dot shown at the top left corner of the screen to signify that the user is editing text.
        if editing:
            draw_highlighted_rect(screen, pygame.Rect(0, 0, 10, 10), (255, 0, 0), (255, 0, 0), 10, 10)
        pygame.display.flip() # Updates display.

    pygame.quit()   

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    tick_img = pygame.image.load("images\\tick_mark.png").convert_alpha() #Reduces lag.
    main(screen)
#--------- Description-----------------------------------------------#
#
#  DILBERT COMIC BROWSER
#
#  Requirements: This is a simple Python program that uses Python
#                Imaging Library (PIL). This program is to be used
#                with Python 2.7.x
#
#  PIL URL:  http://www.pythonware.com/products/pil/
#
#  About:  This project was a task set by myself to help me learn a new
#          a language.  The task was simple, to be able to download 
#          images from another website and display in a local program.
#
#          For the Python GUI I used Tkinter.  URLLib to download the web source.
#          RegEx to parse the text and find what I needed (the comic strips)
#          Lastly, PIL to display the comic strips.
#
#  Author:  Ian Daniel
#
#  NOTE: All photos used are from Dilbert.com and owned by them.
#
#--------------------------------------------------------------------#

from urllib import urlopen
from re import findall, VERBOSE, sub
from Tkinter import * 
from StringIO import StringIO
from PIL import Image, ImageTk


## *******************************************************************
##                  Function definitions
## *******************************************************************

def get_web_site(url_address, num_pages = 4):
    ''' Download the HTML from the provided URL '''
    if num_pages == 1:
        open_page = urlopen(url_address)
        return_raw_code = open_page.read()
        open_page.close()
    else:
        return_raw_code = ''
        for each in range(1,num_pages+1):
            if each == 1:
                url_extra = ''
            else:
                #url_extra = '?starting_point=' + str((each*4-3))
                url_extra = '?starting_point=' + str((each*2+(each-3)))
                
            open_page = urlopen(url_address + url_extra)

            # Display the progress of downloading the webpage
            percent_done = str(int((float(each)/(num_pages+1))*100))
            print "  " + percent_done + "% done..."
            
            raw_code = open_page.read()
            return_raw_code = return_raw_code + raw_code
            open_page.close()
            
    print " 100% done..."
    print
    print "Displaying window.."
    return return_raw_code

def logo_img_url(source_data):
    '''  Find and return the URL for the main logo  '''
    
    logo_list = findall('''logo-container["><a-zA-Z= ]+
                href="([.a-z:/]+)[.a-zA-Z0-9"><=:/\n\s-]+
                src="/([.a-z0-9/-]+)"  
                ''',source_data, VERBOSE)

    logo_url = logo_list[0][0] + logo_list[0][1]            
    
    return logo_url

def clean_title(dirty_title):
    ''' Remove HTML codes for some characters '''
    dirty_list = (["&#39;","'"],
                  ["&amp;",'&'],
                  ["&#38;",'&'],
                  ["&#34;",'"'],
                  ["&quot;",'"'])

    for list_item in dirty_list:
        dirty_title = sub(list_item[0], list_item[1], dirty_title)
        
    return dirty_title

def reverse_date(US_date):
    ''' Change the US Date format to Australian '''
    split_date = findall('([0-9]+)-([0-9]+)-([0-9]+)', US_date)
    AUS_date = split_date[0][2] + "-" + split_date[0][1] + "-" + split_date[0][0]
    
    return AUS_date

def rip_data(source_data):
    '''
    Input: source_data
        Expects the HTML from a dilbert.com
    
    Output: return_me[x][y]
        x = The day the comic was released
          0 for today, 4 for 5 days ago
        y = The 3 types of data that can be used
          0 - date
          1 - Comic strip title
          3 - Comic strip GIF image URL
    '''

    return_me = findall('''img-comic-container[.a-zA-Z0-9"><=:/\n\s-]+
                            href="[.a-z:/]+([0-9-]+)[.#&;a-zA-Z0-9"><=:/\n\s-]+
                            alt="([#&;0-9a-zA-Z ]+)[.a-zA-Z0-9"><=:/\n\s-]+
                            src="([.#&;a-z0-9:/]+)"
                        ''',source_data, VERBOSE)

    # Delete the last 2 images and then reverse order to show oldest first
    return_me = return_me[:-2][::-1]  

    return return_me


def prev_next_button(button_action, jump_number = 'none'):
    global current_img_index
    global processed_data
    number_of_images = (len(processed_data) - 1)

    update_image = 0
    
    # Right column Skip to data area
    if jump_number != 'none':
        if current_img_index == 'Logo':
            button_action = 'next'
            if jump_number == 0:
                jump_number = 0
            else:
                current_img_index = jump_number - 1
        elif jump_number < current_img_index:
            comic_date[current_img_index]['font'] = ('Arial', 12)
            current_img_index = jump_number + 1
            button_action = 'prev'
        elif jump_number == current_img_index:
            pass
        elif jump_number > current_img_index:
            button_action = 'next'
            comic_date[current_img_index]['font'] = ('Arial', 12)
            current_img_index = jump_number - 1

    # Get new image index number ready
    if current_img_index == 'Logo':
        current_img_index = 0
        update_image = 1
    elif button_action == 'prev' and current_img_index > 0:
        comic_date[current_img_index]['font'] = ('Arial', 12)
        next_button.configure(state='normal')
        next_button.configure(cursor='hand2')
        current_img_index -= 1
        update_image = 1
        if current_img_index == 0:
            previous_button.configure(state='disable')
            previous_button.configure(cursor='arrow')
    elif button_action == 'next' and current_img_index < number_of_images:
        comic_date[current_img_index]['font'] = ('Arial', 12)
        previous_button.configure(state='normal')
        previous_button.configure(cursor='hand2')
        current_img_index += 1
        update_image = 1
        if current_img_index == number_of_images:
            next_button.configure(state='disable')
            next_button.configure(cursor='arrow')

    # Only change image if it is new
    if update_image:
        # Open image from URL
        reference_to_comic = urlopen(processed_data[current_img_index][2])
        stringed_reference = StringIO(reference_to_comic.read())
        img_opened = Image.open(stringed_reference)
        reference_to_comic.close()

        # Resize
        image_resize = 920,300 
        img_opened.thumbnail(image_resize, Image.ANTIALIAS)

        # Prepair for and sent to Tkinter
        prepaired_image = ImageTk.PhotoImage(img_opened)
        image_panel.configure(image = prepaired_image)
        image_panel.image = prepaired_image

        # Set new comic title under the image or blank it if not givern
        if processed_data[current_img_index][1] == " ":
            comic_title['text'] = ""
        else:
            comic_title['text'] = '"' + clean_title(processed_data[current_img_index][1].rstrip()) + '"'

        # Make date bold
        comic_date[current_img_index]['font'] = ('Arial', 16)
        

def ex_button():
    ''' Graceful exit of the program '''
    browser_window.destroy()

def opening_logo(source_data):
    ''' Find, open and resize the logo on dilbert.com '''

    # Find and open
    reference_to_logo = urlopen(logo_img_url(source_data))
    stringed_reference = StringIO(reference_to_logo.read())
    img_opened = Image.open(stringed_reference)

    # Resize
    set_width = 200
    width_percent = (set_width/float(img_opened.size[0]))
    height_size = int((float(img_opened.size[1])*float(width_percent)))
    img_opened = img_opened.resize((set_width,height_size), Image.ANTIALIAS)

    # Prepair for Tkinter
    return_img_opened = ImageTk.PhotoImage(img_opened)

    return return_img_opened

## *******************************************************************
##                  End Function definitions
## *******************************************************************
##                  Start Program
## *******************************************************************


# Just show something in the main window so
# the user knows the program hasn't crashed

print "Your Internet connection speed will determin how long this will take."
print
print "Loading from the web - Please wait..."
print
print "   0% done..."

## *******************************************************************
##                  Setup the Tkinter window 
## *******************************************************************

browser_window = Tk()
browser_window.title('Dilbert Comic Strip Viewer by Ian Daniel')

current_img_index = 'Logo'


## *******************************************************************
##                  Downloads new copy of Dilbert.com
##                  and set starter image
## *******************************************************************

dilberts_url = "http://dilbert.com/"
found_error = 0

try:
    raw_data = get_web_site(dilberts_url)
    processed_data = rip_data(raw_data)
    starter_img = opening_logo(raw_data)
    
except:
    found_error = 1
    starter_img = ""
    processed_data = ""
    print
    print "  Error accessing the Internet."
    print "  Please check you Internet connection before trying again"

## *******************************************************************
##                  Build background 
## *******************************************************************
    
left_bg_col = '#EFFCFF'
right_bg_col = '#FFFFEF'

left_bg = Frame(browser_window, height=400, width=924, bd=0, relief=FLAT,
                bg=left_bg_col)
divider1 = Frame(browser_window, height=400, width=1, bd=0, relief=FLAT,
                 bg='#ACC1C7')
divider2 = Frame(browser_window, height=400, width=1, bd=0, relief=FLAT,
                 bg='#5C5C5C')
divider3 = Frame(browser_window, height=400, width=1, bd=0, relief=FLAT,
                 bg='#D2D2B9')
right_bg = Frame(browser_window, height=400, width=164, bd=0, relief=FLAT,
                 bg=right_bg_col)

left_bg.pack(side=LEFT)
divider1.pack(side=LEFT)
divider2.pack(side=LEFT)
divider3.pack(side=LEFT)
right_bg.pack(side=LEFT)


## *******************************************************************
##                  Build widgets 
## *******************************************************************

title_field = Label(left_bg, text='Dilbert Comic Strip Browser',
                    font=('Comic Sans MS', 25), bg = left_bg_col)

image_panel = Label(left_bg, image = starter_img, bg = left_bg_col,
                    width=920, height=300)

previous_button = Button(left_bg, text='Previous', width=10,
                         font=('Arial', 14), state='disable', cursor='arrow',
                         command = lambda: prev_next_button('prev'))

next_button = Button(left_bg, text='Next', cursor='hand2',
                         font=('Arial', 14), width=10,
                         command = lambda: prev_next_button('next'))

comic_title = Label(left_bg, text='', bg = left_bg_col, width = 70,
                    font=('Arial', 12), justify=CENTER)

skip_to_title = Label(right_bg, bg=right_bg_col, text='Skip to date',
                      font=('Arial', 15))

skip_to = Frame(right_bg, bg='#FFFFDF', width = 140, height = 280,
                highlightbackground='#D3D343', highlightthickness=1)

# List all the comic dates retrieved from dilbert.com
comic_date = {}
for counter in range(len(processed_data)):
    comic_date[counter] = Button(skip_to, text=reverse_date(processed_data[counter][0]),
                                bg='#FFFFDF', activebackground = '#FFFFDF',
                                font=('Arial', 12), bd = 0, cursor='hand2',
                                command = lambda new_counter=counter: prev_next_button('jump', new_counter))

exit_button = Button(right_bg, text='Exit', cursor='hand2',
                     font=('Arial', 14), width=10,
                     command = lambda: ex_button())


## *******************************************************************
##                  Place widgets into window
## *******************************************************************

title_field.place(x=240, y=5)
image_panel.place(x=0, y=50)
previous_button.place(x=11, y=352)
comic_title.place(x=143, y=359)
next_button.place(x=792, y=352)
skip_to_title.place(x=26, y=32)
skip_to.place(x=12, y=62)
exit_button.place(x=22,y=352)

# Fill the 'Skip to date' frame with dates
for counter in range(len(processed_data)):
    comic_date[counter].place(x=68, y=22+(counter*26), anchor="center")

if found_error:
    error_frame = Frame(browser_window, height=400, width=1091, bd=0,
                        relief=FLAT, bg="white")
    error_frame.place(x=1,y=1)
    error_text = Label(error_frame,text = '''Error accessing the Internet. \n Please check you Internet connection before trying again.
                        ''', bg = "white", font=('Ariel', 25), justify= CENTER)
    error_text.place(x = 125, y = 150)

# Start the Dilbert event loop
browser_window.mainloop()


#
#---------------- End Program----------------------------------------#
#

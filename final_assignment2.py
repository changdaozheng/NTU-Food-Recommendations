##################################################################################
# RE1016 Engineering Computation Assignment 2 - Computational Thinking with Python
# Done By: Chang Dao Zheng  
# Matric Number:  
# Latest Revision: 25th Mar 2022
##################################################################################

###################################
#Section 0: Import external modules
###################################
from PIL import Image
import pandas as pd
import warnings
import pygame
import time
import re


####################################
#Section 1: Load and initialise data
#################################### 
filepath = "canteens.xlsx"
main_df = pd.read_excel(filepath, index_col="Unnamed: 0")
main_df =  main_df.applymap(lambda x: x.lower() if pd.notnull(x) and type(x) == str else x) #Shift all words into lowercase to allow for non-case sensitive comparison with user inputs 
main_df["Keywords"] = main_df["Keywords"].apply(lambda x: x.split(", ")) #Cast Keywords series into a list
main_df["Location"] = main_df["Location"].apply(lambda x: tuple(x.split(","))) #Cast Locations series into a tuple 


##########################
#Section 2: Main Functions
##########################
def main():
    
    while True:
        print("\n=======================")
        print("F&B Recommendation Menu")
        print("1 -- Display Data")
        print("2 -- Keyword-based Search")
        print("3 -- Price-based Search")
        print("4 -- Location-based Search")
        print("5 -- Exit Program")
        print("=======================")

        #Input error handling
        mode = input("Enter option [1-5]: ")
        try: 
            mode = int(mode)
        except: 
            print("Please enter an integer from 1-5!\n")
            continue

        if mode == 1:
            # print dataframe structures 
            print("\n=================\n1 -- Display Data\n=================")
            print("\nKeyword Dataframe: \n", main_df.loc[:,["Canteen", "Stall", "Keywords"]], "\n")
            print("\nPrice Dataframe: \n", main_df.loc[:,["Canteen", "Stall", "Price"]])
            print("\nLocation Dataframe: \n", main_df.loc[:,["Canteen", "Location"]])
        
        elif mode == 2:
            # keyword-based search
            print("\n=========================\n2 -- Keyword-based Search\n=========================")
        
            # call keyword-based search function
            keyword_arr, result_df = keyword_matching()
            search_by_keyword(keywords = keyword_arr, result_df = result_df)
           

        elif mode == 3:
            # price-based search
            print("\n=======================\n3 -- Price-based Search\n=======================")

            # call price-based search function
            keyword_arr, result_df = keyword_matching() #Returns keywords entered and a dataframe of rows that matches keywords entered

            #Verify that price input is numerical and is not negative
            while True:
                try:
                    price = float(input("\nEnter maximum meal price (S$):"))
                    if price < 0: 
                        print("Price entered cannot be negative. Please try again")
                        continue
                    else: break
                except: 
                    print("\nPlease enter a numerical value.")
                    continue

            search_by_price(keywords = keyword_arr, max_price = price, result_df = result_df)

        elif mode == 4:
            # location-based search
            print("\n==========================\n4 -- Location-based Search\n==========================")

            # call PyGame function to get two users' locations
            starting_pt_arr = []
            for i in range(2):
                coordinates = get_user_location_interface()
                starting_pt_arr.append(coordinates)
            
            #Print user location
            print("User A: ", str(tuple(starting_pt_arr[0])))
            print("User B: ", str(tuple(starting_pt_arr[1])))


            #Error handling for number of canteens required 
            while True: 
                try: 
                    num_canteens =  int(input("\nNumber of canteens required: "))
                    if num_canteens <= 0:
                        print("\nNumber of canteens cannot be less than 1! Returning 1 nearest canteen...")
                        num_canteens = 1
                    break
                except: 
                    print("Please enter a positive number.")
                    continue

            # call location-based search function          
            search_nearest_canteen(user_location = starting_pt_arr, k = num_canteens)

        elif mode == 5:
            # exit the program
            print("Exiting F&B Recommendation")
            break


def search_by_keyword(keywords, result_df): 
    #Returns keywords entered and a dataframe of rows that matches keywords entered
    formatted_output(df = result_df, mode = 2) #Output results


def search_by_price(keywords,max_price,result_df): 
   
    #Returns dataframe that matches max price and keywords if keywords are valid, or else return a dataframe that matches max price only
    if result_df.empty: #Error handling when keywords entered yields no results
        print("\nType of food not found in database, returning closest priced item...")
        result_by_price_df = main_df[main_df['Price'] <= max_price].max().to_frame().transpose() #Returns the closest priced item if no keywords match
        result_by_price_df['num_matched'] = 0 
    else:
        result_by_price_df = result_df[result_df['Price'] <= max_price].sort_values(by="Price") #Returns a dataframe of rows that have prices less than or equaled to user entered maximum price and matches keywords entered
        if result_by_price_df.empty: #Error Handling when price entered yield no results for the type of food selected
            print("\nNo food stall found with specified price range, returning closest priced item that matches keywords...")
            result_by_price_df = result_df.sort_values(by='Price').iloc[0,:].to_frame().transpose() #Returns the cheapest item that matches keywords if no food items matches keywords and falls within the max price range requested by user
    formatted_output(df = result_by_price_df, mode = 3) #Output results
    

def search_nearest_canteen(user_locations, k): 
    canteen_df = main_df.loc[:,["Canteen", "Location", "Stall"]].groupby(["Canteen", "Location"]).agg(", ".join).reset_index() #Groups dataframe by canteen while aggregating stalls to a string that can be accessed if needed
    canteen_df["Distance from A"] = canteen_df["Location"].apply(lambda x: euclidean_d(x, user_locations[0])) #Distance from user A to each canteen
    canteen_df["Distance from B"] = canteen_df["Location"].apply(lambda x: euclidean_d(x, user_locations[1])) #Distance from user B to each canteen

    canteen_df = canteen_df.sort_values(by=["Distance from A","Distance from B"], ascending=(True, True)) #Sort dataframe based on distance from A and B (prioritises distance from A)
    result_df = canteen_df.iloc[:k].reset_index()
   
    formatted_output(df = result_df , mode = 4) #Output Results


############################
#Section 3: Helper Functions
############################
#Process keywords from user input as well as conditions(or/and) specified by the user and returns an array of those keywords and the condition combining them; used for modes 2 and 3
def keyword_input_handling():
    while True:
        keyword_input = input("\nEnter type of food: ")

        #Rejecting inputs that are empty or only filled with spaces
        if re.match("^\s*$", keyword_input):
            print("No input found. Please try again.")
            continue
        
        #Rejecting inputs that contains non-alphabetic characters since all keywords are alphabetic 
        if not re.match(r"^[\sa-zA-Z-;,.+]+$", keyword_input): 
            print("Invalid food type! Please try again.")
            continue
        
        #Cast keywords entered into a list by considering multiple seperators using regex
        keyword_arr = re.split(r"[-;,.+\s]\s*", keyword_input.strip().lower())
        if "mixed" in keyword_arr and "rice" in keyword_arr: 
            keyword_arr.remove("mixed")
            keyword_arr.remove("rice")
            keyword_arr.append("mixed rice")
        
        
        #Checking for conditions(and/or) and removing them from the input; only accepts all "and" conditions or all "or" conditions
        condition = ''
        if "and" in keyword_arr or ("or" not in keyword_arr and len(keyword_arr)>1): 
            keyword_arr = list(filter(lambda x: x != "and", keyword_arr)) #removes all occurences of "and" from the keyword arr
            condition = "and"
            
        elif "or" in keyword_arr:
            keyword_arr = list(filter(lambda x: x != "or", keyword_arr))#removes all occurences of "or" from the keyword arr
            condition = "or"

        return keyword_arr, condition


#Returns a dataframe of stalls that matches keywords entered; used for modes 2 and 3
def keyword_matching():
    keyword_arr, condition = keyword_input_handling()

    if condition == "and": 
        result_df = main_df.loc[main_df["Keywords"].apply(lambda row: all(keyword in row for keyword in keyword_arr))] #Returns a dataframe of rows that contains all the entered keywords
    elif condition == "or":
         result_df = main_df.loc[main_df["Keywords"].apply(lambda row: any(keyword in row for keyword in keyword_arr))] #Returns a dataframe of rows that contains at least 1 of the entered keywords
    else: #Placed in a separate else statement for clarity, can be combined with the if statment since both conditions lead to the same block
        result_df = main_df.loc[main_df["Keywords"].apply(lambda row: all(keyword in row for keyword in keyword_arr))] #Returns a dataframe of rows that contains the entered keyword 
    
    warnings.filterwarnings('ignore')
    result_df['num_matched'] = result_df.loc[:,'Keywords'].apply(lambda row: sum(keyword in row for keyword in keyword_arr)) #Count number of keywords matched for each food store
    return keyword_arr,result_df


#Print results based on requested formats; used for modes 2,3 and 4
def formatted_output(df, mode):

    #Print results of query as long as dataframe returned is not empty 
    if not df.empty:
        print("\nFood Stalls Found: ", str(len(df.index)))

        if mode in (2,3):
            unique_matches = list(set(df['num_matched'])) #find out unique number of keywords matched across all results returned (to deal with "or" case when not all rows matches all keywords entered)
            for i in unique_matches: #i represents number of keywords matched 
                if i != 0: #Only inform users of the number of keywords matched when at least 1 keyword is valid and the query has valid results
                    print("\nFood stalls that matches {} keyword(s):".format(i))
                i_matches_df = df[df['num_matched']==i] #returned a dataframe of rows with i number of keywords matched 
                for index, row in i_matches_df.iterrows():
                    canteen = " ".join(x.capitalize() for x in row["Canteen"].split(" ") if type(x) == str) #Capitalise first letter of all words
                    stall = " - " + " ".join(x.capitalize() for x in row["Stall"].split(" ") if type(x) == str)#Capitalise first letter of all words
                    
                    price_formatting = " - S${:.2f}".format(row["Price"])
                    print("{canteen}{stall}{price}".format(canteen = canteen, stall = stall, price = price_formatting if mode == 3  else "")) #Only output price of food if 3rd Option is selected
        elif mode == 4: 
            print("\nFood Stalls Nearby:")
            for index, row in df.iterrows():
                distanceA =  " - Distance from user A: " + str(round(int(row["Distance from A"]))) +"m"
                distanceB =  " - Distance from user B: " + str(round(int(row["Distance from B"]))) +"m"
                distance = distanceA + distanceB

    #Inform the user that the program is unable to find a match or give a nearest recommendation based on the information entered
    else:  
        print("No food stalls found. Please refer to option 1 to find valid keywords.\n")


#Returns coordinates of user selected locations; used for mode 4
def get_user_location_interface():
    # get image dimensions
    image_location = 'NTUcampus.jpg'
    pin_location = 'pin.png'
    screen_title = "NTU Map"
    image = Image.open(image_location)
    image_width_original, image_height_original = image.size
    scaled_width = int(image_width_original)
    scaled_height = int(image_height_original)
    pinIm = pygame.image.load(pin_location)
    pinIm_scaled = pygame.transform.scale(pinIm, (60, 60))
    # initialize pygame
    pygame.init()
    # set screen height and width to that of the image
    screen = pygame.display.set_mode([scaled_width, scaled_height])
    # set title of screen
    pygame.display.set_caption(screen_title)
    # read image file and rescale it to the window size
    screenIm = pygame.image.load(image_location)

    # add the image over the screen object
    screen.blit(screenIm, (0, 0))
    # will update the contents of the entire display window
    pygame.display.flip()

    # loop for the whole interface remain active
    while True:
        # checking if input detected
        pygame.event.pump()
        event = pygame.event.wait()
        # closing the window
        if event.type == pygame.QUIT:
            pygame.display.quit()
            mouseX_scaled = None
            mouseY_scaled = None
            break
        # resizing the window
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.dict['size'], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            screen.blit(pygame.transform.scale(screenIm, event.dict['size']), (0, 0))
            scaled_height = event.dict['h']
            scaled_width = event.dict['w']
            pygame.display.flip()
        # getting coordinate
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # get outputs of Mouseclick event handler
            (mouseX, mouseY) = pygame.mouse.get_pos()
            # paste pin on correct position
            screen.blit(pinIm_scaled, (mouseX - 25, mouseY - 45))
            pygame.display.flip()
            # return coordinates to original scale
            mouseX_scaled = int(mouseX * 1281 / scaled_width)
            mouseY_scaled = int(mouseY * 1550 / scaled_height)
            # delay to prevent message box from dropping down
            time.sleep(0.2)
            break
    pygame.quit()
    pygame.init()
    return [mouseX_scaled, mouseY_scaled]


#Returns the euclidean distance between 2 points, takes 2 sets of coordinates as function argument; used for mode 4
def euclidean_d(pt1, pt2):
    return ((int(pt1[0])-int(pt2[0]))**2 + (int(pt1[1])-int(pt2[1]))**2)**0.5


main()

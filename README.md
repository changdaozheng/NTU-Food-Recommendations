# RE1016 Engineering Computation Assignment 2 - Computational Thinking with Python 

## Section 0: Import External Modules 
Imported python libraries 
- PIL 
- pandas
- warnings 
- pygame 
- time 
- re 
<br/><br/>

## Section 1: Load and Initialise data 
Load given data with Pandas and stored them in a dataframe instead of the given data structure. Manipulated the data for querying functions in later sections. 
<br/><br/>

## Section 2: Main Functions
Contains the main functions for this task. 

- main
    - Controls the logic overall logic flow and user experience for the program 

- search_by_keyword
    - First function required by the assignment. Main function will access this function to allow users to search for the relevant food store based on the inputs that they have entered. 

- search_by_price
    - Second function required by the assignment. Main function will access this function to allow users to search for relevant food stores up to a certain maximum price based on the inputs that they have entered.

- search_nearest_canteen
    - Third function required by the assingment. Main function will access this function to allow users to search for the relevant food stores based on their location. The function will prioritise the location of the first user when giving recommendations. 
<br/><br/>

## Section 3: Helper Functions
Extra functions added that are used across the 4 functions in **Section 2**. 
- keyword_input_handling 
    - Process keywords from users' input and returns an array of the keywords entered and the condition joining these keywords. Only one condition should be entered per user input. 
    - Rejects all inputs that are invalid 
        - Spaces only 
        - Empty inputs 
        - Numbers (since there are no numbers in the keywords given)
        - Special characters (!, ?, % ,#, etc.)

- keyword_matching
    - Main querying function that returns an array of the keywords queried and a dataframe containing the food stalls that matches the user's requests 

- formatted_output
    - Main output printing function that prints out the query results based on the recommendation option selected by the user

- get_user_location_interface
    - Returns coordinates of user selected locations in mode 4

- euclidean_d 
    - Returns the distance between 2 points 
    


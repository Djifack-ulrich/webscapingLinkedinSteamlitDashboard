# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import streamlit as st
import plotly.express as px

def scrape_linkedin_events(search_query, nb_page):
    # Replace with the path to your WebDriver executable
    webdriver_path = '/path/to/your/chromedriver'

    # Browser options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # If you don't want to see the browser opening

    # Initialize the browser
    driver = webdriver.Chrome()

    # Wait for up to 10 seconds for the page to load
    wait = WebDriverWait(driver, 1000)

    data = []

    for i in range(1, nb_page + 1):
        try:
            driver.get(f"https://www.linkedin.com/search/results/events/?keywords={search_query}&page={i}")
            # Wait for the search results to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'reusable-search__result-container')))

            # Extract the data
            events = driver.find_elements(By.CLASS_NAME, 'reusable-search__result-container')

            for event in events:
                title = event.find_element(By.CLASS_NAME, 'entity-result__title-text').text.strip()
                date = event.find_element(By.CLASS_NAME, 'entity-result__primary-subtitle').text.strip()
                location_info = event.find_element(By.CLASS_NAME, 'entity-result__secondary-subtitle').text.strip()
                attendees_info = event.find_element(By.CLASS_NAME, 'reusable-search-simple-insight__text').text.strip()
                link = event.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                # Check if the summary is present
                summary_element = event.find_elements(By.CLASS_NAME, 'entity-result__summary')
                summary = summary_element[0].text.strip() if summary_element else ''

                data.append({
                    'Event': title,
                    'Date': date,
                    'Location': location_info,
                    'Attendees': attendees_info,
                    'Summary': summary,
                    'Link': link
                })
        except:
            break

    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    df["Attendees"] = df["Attendees"].apply(lambda x: int((x.split()[0]).replace(',','')))
    return df

# Function to display top N events based on attendees
def display_top_events(data, n):
    st.subheader(f'Top {n} Events based on Attendees')
    top_events = data.nlargest(n, 'Attendees')
    st.table(top_events[['Event', 'Attendees']])
    return top_events

# Streamlit Dashboard
st.title("LinkedIn Events Dashboard")

# Allow user to input a search query
search_query = st.sidebar.text_input('Enter a search query:')
if not search_query:
    st.warning("Please enter a search query.")
else:
    # Example usage with the user-input search query
    data = scrape_linkedin_events(search_query, 5)

    # Display the total number of events
    st.sidebar.info(f'Total Number of Events: {len(data)}')

    # Display the DataFrame
    st.subheader('LinkedIn Events Data')
    st.dataframe(data)

    # Allow user to input a keyword
    keyword = st.sidebar.text_input('Enter a keyword to filter events:')
    filtered_data = data[data['Event'].str.contains(keyword, case=False, na=False)]

    # Display filtered events
    if not filtered_data.empty:
        st.subheader(f'Filtered Events containing "{keyword}"')
        st.dataframe(filtered_data)
    else:
        st.warning(f'No events found with keyword "{keyword}".')

    # Allow user to input the number of top events to display
    num_top_events = st.sidebar.number_input('Enter the number of top events to display:', min_value=1, max_value=len(data), value=5)

    # Display the top N events based on attendees
    top_events = display_top_events(data, num_top_events)

    # Redirect to the LinkedIn event page when clicking on the top events
    for index, row in top_events.iterrows():
        event_link = row['Link']
        if st.button(f"Open {row['Event']}"):
            st.sidebar.success(f"Redirecting to {row['Event']} on LinkedIn...")
            st.markdown(f"Redirecting to [LinkedIn Event]({event_link})...")
            # Add any additional actions for redirection if needed (e.g., web browser open link)

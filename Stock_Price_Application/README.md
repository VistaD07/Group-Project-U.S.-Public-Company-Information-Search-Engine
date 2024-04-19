# Company Info Application

## Overview
The Company Info Application is designed to provide users with tailored financial information based on specific ticker symbols and information types. Users can select various variables and time frames to retrieve personalized data displays.

## Features
- **User-defined Data Selection**: Choose data based on ticker and info type.
- **Customization**: Customize variables and time periods for data display.

## Prerequisites
To run this application, you will need the following Python packages:
- Flask
- pandas
- psycopg2

Additionally, data is acquired from WRDS and can be cleaned and imported into a SQL database using the provided `project_code.ipynb` notebook.

## Installation
1. Clone the repository to your local machine.
2. Ensure that you have Python installed, along with the necessary packages listed above.
3. Navigate to the project folder and install the required dependencies.

## Usage
To start the application:
1. Navigate to the `Company_Info_Application` project folder in your terminal.
2. Run `app.py` using the following command:
3. Access the application through your web browser at the specified Flask server address (usually http://127.0.0.1:5000/).

## Data Cleaning
Follow the steps in `project_code.ipynb` to clean the data from WRDS and import it into your SQL database.

## Contribution
Contributions to this project are welcome. Please send pull requests for any improvements you make.

## License
Specify the license under which the project is made available.

## Contact
For any queries or bug reports, please create an issue in the repository.

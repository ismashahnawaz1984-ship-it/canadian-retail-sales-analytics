import pandas as pdimport requests


Purpose:
- pandas = work with tables/data
- requests = pull data from a web source/API
This will make the process easier to follow cell by cell.
Step 5 — Inspect the dataset structure
Run:
df.shape


Then:
df.columns.tolist()


Purpose:  
- df.shape tells us how many rows and columns we have.
- df.columns.tolist() shows the exact column names before we clean anything.
This prevents us from guessing and wasting time.
df.head(20)


shows the first 20 rows of the whole dataset.
In our code:
df[['Sales', 'Adjustments', 'UOM', 'SCALAR_FACTOR']].drop_duplicates().head(20)


it does three things:
1. Selects those 4 columns.
2. drop_duplicates() removes repeated combinations.
3. head(20) shows only the first 20 unique combinations.
Purpose: we don't need to look at thousands of rows. We just want a quick look at what kinds of values exist.
You can also use:
df.head(5)


for 5 rows, or:
df.head(50)


for 50 rows.
df['GEO'].drop_duplicates()


means:
Show me every different geography value only once.

Why we did this
We now know the dataset contains both:
- country/province-level data
- some city-level data
Before building Power BI visuals, we need to decide whether to keep all of them or focus mainly on provinces and Canada totals.
Next, run:
df['North American Industry Classification System (NAICS)'].drop_duplicates().head(30)


Purpose: to see what retail categories/industries are available.
df['REF_DATE'].min(), df['REF_DATE'].max()


Purpose:
This tells us the earliest and latest month/year in the dataset so we know how much historical data we have.
Then run:
df['REF_DATE'].head()


Purpose:
This shows us the date format so we know how to convert it properly for Python and Power BI.
Step 7 — convert the date column
Run:
df['REF_DATE'] = pd.to_datetime(df['REF_DATE'], format='%Y-%m')


Then:
df['REF_DATE'].head()


Purpose:
This converts values like 2017-01 into a real date field so Python can correctly calculate trends, growth rates, moving averages, and other statistics.
You should now see dates like:
2017-01-01
Step 8 — check for missing values
Run:
df.isnull().sum()


Purpose:
This tells us how many blank/null values exist in each column.
Step 9 — inspect rows where VALUE is blank
Run:
df[df['VALUE'].isnull()][    ['REF_DATE', 'GEO', 'North American Industry Classification System (NAICS)',     'Sales', 'Adjustments', 'STATUS']].head(20)


Purpose:
This shows us examples of rows where the sales value is missing. We need to determine whether they are legitimately unavailable/suppressed data or bad records.
Step 10 — remove rows where VALUE is missing
Run:
df_clean = df.dropna(subset=['VALUE'])


Then check the new size:
df_clean.shape


Purpose:
We create a cleaned dataset that keeps only rows where an actual sales value exists, while preserving the original df untouched.
Step 11 — keep only useful columns
Run:
df_clean = df_clean[    [        'REF_DATE',        'GEO',        'North American Industry Classification System (NAICS)',        'Sales',        'Adjustments',        'UOM',        'SCALAR_FACTOR',        'VALUE'    ]]


Then:
df_clean.head()


Purpose: We’re removing technical Statistics Canada metadata like VECTOR, COORDINATE, SYMBOL, etc. They won't help our statistical analysis or Power BI dashboard.
We are not renaming anything yet.
Step 12 — check the data types
Run:
df_clean.dtypes


Purpose:
Before doing statistics, we need to confirm that:
- REF_DATE is a date
- VALUE is numeric
- the other fields are text
Step 13 — check the unit scaling
Run:
df_clean['SCALAR_FACTOR'].drop_duplicates()


Purpose:
Your VALUE field may be stored in units like thousands of dollars. Before calculating totals, averages, or trends, we need to confirm the scale so we interpret the numbers correctly.
Step 14 — create an actual dollar value column
Run:
df_clean['Sales_Dollars'] = df_clean['VALUE'] * 1000


Then:
df_clean[['VALUE', 'Sales_Dollars']].head()


Purpose:
This gives us a business-friendly sales field in actual dollars, which will make Power BI KPIs easier to understand and format.
The Sales_Dollars values are showing in scientific notation, for example:
4.137701e+10

That means:
$41,377,010,000
Nothing is wrong with the data — pandas is just shortening very large numbers.
Step 15 — make the numbers easier to read
Run:
pd.options.display.float_format = '{:,.2f}'.format


Then:
df_clean[['VALUE', 'Sales_Dollars']].head()


Purpose:
This changes only how pandas displays the numbers. It does not change the actual data.
You should now see values like:
41,377,010.00
41,377,010,000.00
Step 16 — start the statistical analysis
Run:
df_clean['Sales_Dollars'].describe()


Purpose:
This gives us the basic descriptive statistics for sales:
- count
- mean
- standard deviation
- minimum
- 25th percentile
- median
- 75th percentile
- maximum
This is the first real statistical analysis in the project and will help us understand the spread of retail sales values.
Step 17 — create a monthly retail-sales trend table
Run:
monthly_sales = (    df_clean[        (df_clean['GEO'] == 'Canada') &        (df_clean['Sales'] == 'Total retail sales') &        (df_clean['Adjustments'] == 'Seasonally adjusted') &        (df_clean['North American Industry Classification System (NAICS)'] == 'Retail trade [44-45]')    ]    [['REF_DATE', 'Sales_Dollars']]    .sort_values('REF_DATE'))monthly_sales.head()


Purpose:
Right now your dataset contains many geographies, industries, and measure types. This code creates one clean national monthly time series:
Canada → Total Retail Sales → Seasonally Adjusted → Overall Retail Trade
That will be the base for growth rates, moving averages, trend analysis, and later Power BI visuals.
Step 17 — create a monthly retail-sales trend table
Run:
monthly_sales = (    df_clean[        (df_clean['GEO'] == 'Canada') &        (df_clean['Sales'] == 'Total retail sales') &        (df_clean['Adjustments'] == 'Seasonally adjusted') &        (df_clean['North American Industry Classification System (NAICS)'] == 'Retail trade [44-45]')    ]    [['REF_DATE', 'Sales_Dollars']]    .sort_values('REF_DATE'))monthly_sales.head()


Purpose:
Right now your dataset contains many geographies, industries, and measure types. This code creates one clean national monthly time series:
Canada → Total Retail Sales → Seasonally Adjusted → Overall Retail Trade
That will be the base for growth rates, moving averages, trend analysis, and later Power BI visuals
Step 18 — calculate month-over-month growth
Run:
monthly_sales['MoM_Growth_%'] = (    monthly_sales['Sales_Dollars']    .pct_change() * 100)monthly_sales.head()


Purpose:
pct_change() compares each month with the previous month.
A few examples from your output:
- Feb 2017: -1.10%
- Mar 2017: +0.15%
- Apr 2017: +1.78%
- May 2017: -0.23%
That means retail sales decreased or increased compared with the prior month.
The NaN for January is expected because there is no December 2016 row in this filtered series to compare against.
Step 19 — calculate year-over-year growth
Run:
monthly_sales['YoY_Growth_%'] = (    monthly_sales['Sales_Dollars']    .pct_change(periods=12) * 100)monthly_sales.head(15)


Purpose:
Month-over-month can be noisy. Year-over-year compares each month with the same month one year earlier.
Example:
- Jan 2018 vs Jan 2017
- Feb 2018 vs Feb 2017
This is a very common business KPI and will be useful in Power BI.
The first 12 months will show NaN, which is normal.
Step 20 — calculate a 3-month moving average
Run:
monthly_sales['3_Month_Moving_Avg'] = (    monthly_sales['Sales_Dollars']    .rolling(window=3)    .mean())monthly_sales.head(8)


Purpose:
A moving average smooths out short-term ups and downs so we can see the underlying sales trend more clearly.
With a 3-month moving average, each value is based on:
- current month
- previous month
- two months before
The first 2 rows will show NaN because Python does not yet have 3 months of data.
Step 21 — add a 12-month moving average
Run:
monthly_sales['12_Month_Moving_Avg'] = (    monthly_sales['Sales_Dollars']    .rolling(window=12)    .mean())monthly_sales.head(15)


Purpose:
The 12-month moving average gives you the longer-term trend and smooths out seasonal/monthly noise much more than the 3-month average.
Later in Power BI, we can compare:
- Actual Sales
- 3-Month Moving Average
- 12-Month Moving Average
So NaN here does not mean the source data is bad or missing. It means:
“This calculation cannot be made yet because there is not enough historical data.”

Step 22 — calculate short-term volatility
Run:
monthly_sales['3_Month_Volatility_%'] = (    monthly_sales['MoM_Growth_%']    .rolling(window=3)    .std())monthly_sales.head(10)


Purpose:
This measures how much month-to-month growth has been fluctuating over the recent 3 months.
- Higher volatility = sales growth is more unstable
- Lower volatility = sales growth is more consistent
This gives the project a stronger statistical analysis component beyond just growth rates and moving averages.
Step 23 — flag unusual months with a Z-score
Run:
monthly_sales['MoM_Z_Score'] = (    monthly_sales['MoM_Growth_%'] - monthly_sales['MoM_Growth_%'].mean()) / monthly_sales['MoM_Growth_%'].std()monthly_sales['Anomaly_Flag'] = (    monthly_sales['MoM_Z_Score'].abs() >= 2)monthly_sales[    ['REF_DATE', 'MoM_Growth_%', 'MoM_Z_Score', 'Anomaly_Flag']].head(15)


Purpose:
This helps identify months where sales growth was unusually high or unusually low compared with normal behavior.
- Z-score near 0 = normal
- Z-score above 2 or below -2 = unusual
- Anomaly_Flag = True = month worth investigating
Step 24 — export the analyzed data for Power BI
Run:
monthly_sales.to_csv(    r"D:\Retail Analytics with Statistics Power BI Project\Data\monthly_sales_analysis.csv",    index=False)


Then confirm it was created:
import osos.path.exists(    r"D:\Retail Analytics with Statistics Power BI Project\Data\monthly_sales_analysis.csv")


Purpose:
This creates the curated output file that Power BI will consume. At this point, Python has already handled the statistical backend:
- MoM growth
- YoY growth
- 3-month moving average
- 12-month moving average
- volatility
- Z-score
- anomaly flag
If the second command returns True, the file is ready for Power BI.
Time: 1–2 minutes.













false












The most likely issue is the folder path.
Earlier your project folder was:
D:\Retail Analytics with Statistics  Power BI Project\

Notice there are two spaces between Statistics and Power BI.
But in the export code, we used only one space.
Use this exact code instead:
monthly_sales.to_csv(    r"D:\Retail Analytics with Statistics  Power BI Project\Data\monthly_sales_analysis.csv",    index=False)


Then check:
import osos.path.exists(    r"D:\Retail Analytics with Statistics  Power BI Project\Data\monthly_sales_analysis.csv")


Purpose: this exports the final Python analysis into the same Data folder you already used.
You should now get:
True

If it still says False, run this:
os.getcwd()


and send me the output.













true












Perfect. The Python pipeline is now working and the analyzed CSV is ready for Power BI.
Step 25 — load the analyzed CSV into Power BI
In Power BI Desktop:
1. Home → Get Data → Text/CSV
2. Select:
   monthly_sales_analysis.csv
3. Click Transform Data
Purpose:
This connects Power BI to the output of your Python analysis, so Power BI becomes the visualization layer while Python remains the statistical backend.
Once Power Query opens, send me a screenshot of the columns you see.
Step 30 — create the main sales trend chart
Add a Line chart.
Set:
- X-axis: REF_DATE
- Y-axis: Sales_Dollars
Then add these to the same chart as additional values:
- 3_Month_Moving_Avg
- 12_Month_Moving_Avg
Purpose: this lets you compare:
- actual monthly retail sales
- short-term trend
- long-term trend
This is one of the most important visuals in the project because it shows the statistical work from Python directly inside Power BI.
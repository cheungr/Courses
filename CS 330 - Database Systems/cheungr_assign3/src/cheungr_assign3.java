import java.sql.*;
import java.util.*;
import java.text.*;

public class cheungr_assign3 {

	public static void main(String args[]){

        //Defines connection strings to the database using reader account
		Connection con = null;
		String dbname = "jdbc:mysql://db.cs.wwu.edu/CS330_201320";
		String dbuname = "cheungr_reader";
		String dbpassword = "4CxshiQIk";

        //Defines connection strings to the writing database that contains the Temporary Table used to store the data.
        //PLEASE NOTE THAT BECAUSE OF THIS REQUIREMENT, THIS PROGRAM TAKES FOREVER TO RUN. QUERIES EVERYTHING.
        Connection con2 = null;
        String wdbname = "jdbc:mysql://db.cs.wwu.edu/cheungr_CS330";
        String wdbuname = "cheungr_writer";
        String wdbpassword = "2XewEXpCw3";

        //Prepared statements for queries.
        PreparedStatement createTb;
        PreparedStatement writeData;
        PreparedStatement DropTemp;
		PreparedStatement getName;
		PreparedStatement getData;
        PreparedStatement getadjustedData;

        //ResultSets for data retrieved from table queries
		ResultSet tickname;
		ResultSet tickRdata;
		ResultSet adjustedData;

        //String declaration for the ticker name and the day
        String ticker;
		String day;

        //Transaction fee of 8 dollars.
        double transfee = 8.00;

        //Used to make sure input is not an exit command.
		boolean validIn = true;

        //Used to return a correct dollar amount when returning statistics. In the correct Locale structure.
        NumberFormat currencyFormatter = NumberFormat.getCurrencyInstance(Locale.US);

		try{
            //Connects to reader and writer databases
			con = DriverManager.getConnection(dbname, dbuname, dbpassword);
			if(!con.isClosed()){
				System.out.println("Successfully connected to Database " + dbname);
			}
			con2 = DriverManager.getConnection(wdbname, wdbuname, wdbpassword);
            if(!con.isClosed()){
                System.out.println("Successfully connected to Writable DB " + wdbname);
            }

            //Prepared statements for creating, inserting, dropping and getting data of the temporary storage tables.
            createTb = con2.prepareStatement("CREATE TABLE TempStore (TransDate DATE, OpenPrice DOUBLE, ClosePrice Double)");
            writeData = con2.prepareStatement("INSERT INTO TempStore VALUES (?, ?, ?)");
            DropTemp = con2.prepareStatement("DROP TABLE TempStore");
            getadjustedData = con2.prepareStatement("SELECT * FROM TempStore ORDER by TransDate ASC");

            //gets the input for the ticker and verifies if the ticker is a valid input else quits or says it's not right.
			ticker = reader.getInput();
			validIn = reader.verify(ticker);
			
			while (validIn){
                //defines running average with size of 50. Uses the runningavg class
                runningavg movingavg = new runningavg(50);
                //defines all the variables that will be used later.
                double cash = 0.0;
                int shares = 0;
                int transactions = 0;
                double OPrice = 0.0;
                double CPrice = 0.0;
                double NOPrice = 0.0;
                double CNPrice = 0.0;
                double PCPrice = 0.0;
                double multiFactor = 1.00;
                double domath;
                int numDays = 0;

                //creates temp table.
                createTb.execute();

                //Statements that are used to get the company name of the ticker and the date, open and close price of the ticker in descending order.
                getName = con.prepareStatement("SELECT Name FROM company WHERE Ticker = ?");
				getName.setString(1, ticker);
				getData = con.prepareStatement("SELECT TransDate, OpenPrice, ClosePrice FROM pricevolume WHERE Ticker = ? ORDER by TransDate DESC");
				getData.setString(1, ticker);

                //Executes the queries and assigns into tickname and tickRdata.
                tickname = getName.executeQuery();
                tickRdata = getData.executeQuery();

                //This array is used to output the 2:1 splits, etc. (NOT USED FOR ANYTHING OTHER THAN THAT).
                ArrayList<String> arrString = new ArrayList<String>();

                //While the name of the ticker exists
                if (tickname.next()){
                    //Print out the ticker name
                    System.out.println(tickname.getString(1));
                    System.out.println("Adjusting data for splits... (This may takes a while. Grab a cup of tea!)");
                    //While there is a new row in the dataset...
                    while(tickRdata.next()){
                        //Get the date and open price and close price
                        day = tickRdata.getString(1);
                        OPrice = Double.parseDouble(tickRdata.getString(2));
                        CPrice = Double.parseDouble(tickRdata.getString(3));
                        //if the next data exists (This is for the ending last row of the resultset)
                        if (tickRdata.next()) {
                            CNPrice = Double.parseDouble(tickRdata.getString(3));
                            tickRdata.previous();
                        }
                        else {
                            CNPrice = 0;
                        }
                        //Does the next close price / open price, which is then absolute value'd below. To check for splits.
                        domath = CNPrice/OPrice;
                        if (Math.abs(domath - 2.0) < 0.13){
                            String s = "2:1 split on " + day + "; " + CNPrice + " --> " + OPrice;
                            arrString.add(s);
                            multiFactor = multiFactor * 0.50;
                        }
                        else if (Math.abs(domath - 3.0) < 0.13){
                            String s = "3:1 split on " + day + "; " + CNPrice + " --> " + OPrice;
                            arrString.add(s);
                            multiFactor = multiFactor * (1/3);
                        }
                        else if (Math.abs(domath - 1.5) < 0.13){
                            String s = "3:2 split on " + day + "; " + CNPrice + " --> " + OPrice;
                            arrString.add(s);
                            multiFactor = multiFactor * (1/1.5);
                        }
                        //Adjust the price data
                        OPrice = OPrice * multiFactor;
                        CPrice = CPrice * multiFactor;
                        //Write to the table the adjusted data with the day.
                        writeData.setString(1, day);
                        writeData.setDouble(2, OPrice);
                        writeData.setDouble(3, CPrice);
                        writeData.execute();
                    }
                    //Get the adjusted data table into adjustedData
                    adjustedData = getadjustedData.executeQuery();

                    //Clears the previous cash reserve, share reserve, transactions and the day counter.
                    cash = 0.0;
                    shares = 0;
                    transactions = 0;
                    numDays = 0;
                    //While there exists a next row in the dataset
                    while(adjustedData.next()){
                        //Increase the day and get the Close Price and Open Price
                        numDays++;
                        CPrice = Double.parseDouble(adjustedData.getString(3));
                        OPrice = Double.parseDouble(adjustedData.getString(2));
                        //does the last row data compensation
                        if (adjustedData.next()) {
                            NOPrice = Double.parseDouble(adjustedData.getString(2));
                            adjustedData.previous();
                        }
                        else {
                            NOPrice = 0;
                        }
                        //Only when there is at least 51 days
                        if (numDays >= 51){
                            //Get the Previous Close Price
                            adjustedData.previous();
                            PCPrice = Double.parseDouble(adjustedData.getString(3));
                            adjustedData.next();
                            //If the below condition occurs, then buy shares.
                            if (CPrice < movingavg.getAverage() & ((OPrice - CPrice)/OPrice) >= 0.03){
                                shares = shares + 100;
                                cash = cash - (100 * NOPrice);
                                cash = cash - transfee;
                                transactions++;
                                //buys++;
                            }
                            //If the below condition occurs, then sell shares.
                            else if(shares >= 100 & OPrice > movingavg.getAverage() & OPrice > (PCPrice * 1.01)){ //((OPrice - PCPrice)/OPrice) >= 0.01){
                                shares = shares - 100;
                                cash = cash + (100 * ((OPrice + CPrice)/2));
                                cash = cash - transfee;
                                transactions++;
                                //sells++;
                            }
                        }
                        //Calculata da average.
                        movingavg.add(CPrice);
                    }

                    //Print out the Array that contains the strings of the splits.
                    for(int i = 0; i != arrString.size(); i++){
                        System.out.println(arrString.get(i));
                    }

                    if (arrString.size() == 0){
                        System.out.println("\n" + ticker + " does not have any splits. \n");
                    }
                    else{
                        System.out.println("splits: " + arrString.size() + "\n");
                    }
                    //Clear it after printing cause it's used again later
                    arrString.removeAll(arrString);
                    //Outputs the statistics.
                    System.out.println("Executing investment strategy");
                    System.out.println("Transactions executed: " + transactions);
                    System.out.println("Net gain: " + currencyFormatter.format(cash) + "\n");
                    //Drop All The Tables.
                    DropTemp.execute();
                    ticker = reader.getInput();
                }
                else {
                    System.out.println("\n" + ticker + " Does not exist in Database." + "\n");
                    DropTemp.execute();
                    ticker = reader.getInput();
                }
                validIn = reader.verify(ticker);
		}
			System.out.println("! Program has been terminated.");
		} catch (Exception e){
			System.err.println("Exception: " + e.getMessage());
		} finally {
			try{
				if (con != null){
					con.close();
				}
			} catch(SQLException e){}
	
		}
		
	}
	
}
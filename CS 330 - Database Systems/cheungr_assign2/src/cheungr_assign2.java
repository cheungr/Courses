import java.sql.*;
import java.util.*;

public class cheungr_assign2 {

	public static void main(String args[]){
		Connection con = null;
		String dbname = "jdbc:mysql://db.cs.wwu.edu/CS330_201320";
		String dbuname = "cheungr_reader";
		String dbpassword = "4CxshiQIk";
		
		String ticker = null;
		PreparedStatement getName = null;
		PreparedStatement getData = null;
		ResultSet tickname = null;
		ResultSet tickdata = null;
		
		String day = null;
		double NOPrice = 0.0;
		double CPrice = 0.0;
		double domath = 0.0;
		
		boolean validIn = true;
		
		try{
			con = DriverManager.getConnection(dbname, dbuname, dbpassword);
			if(!con.isClosed()){
				System.out.println("Successfully connected to Database " + dbname);
			}
			
			ticker = reader.getInput();
			validIn = reader.verify(ticker);
			
			while (validIn){
				
				getName = con.prepareStatement("SELECT Name FROM company WHERE Ticker = ?");
				getName.setString(1, ticker);
				
				getData = con.prepareStatement("SELECT TransDate, OpenPrice, ClosePrice FROM pricevolume WHERE Ticker = ?");
				getData.setString(1, ticker);
				
				tickname = getName.executeQuery();
				tickdata = getData.executeQuery();
								
				ArrayList<String> arrString = new ArrayList<String>();
				
				if (tickname.next()){
						System.out.println(tickname.getString(1));
						System.out.println("Processing " + ticker + "...");
					while(tickdata.next()){
						day = tickdata.getString(1);
						CPrice = Double.parseDouble(tickdata.getString(3));
						if (tickdata.next()) {
							NOPrice = Double.parseDouble(tickdata.getString(2));
							tickdata.previous();
						}
						else {
							NOPrice = 0;
						}
						domath = CPrice/NOPrice;
						if (Math.abs(domath - 2.0) < 0.13){
							String s = "2:1 split on " + day + "; " + CPrice + " --> " + NOPrice;
							//System.out.println(s);
							arrString.add(s);
						}
						else if (Math.abs(domath - 3.0) < 0.13){
							String s = "3:1 split on " + day + "; " + CPrice + " --> " + NOPrice;
							arrString.add(s);
						}
						else if (Math.abs(domath - 1.5) < 0.13){
							String s = "3:2 split on " + day + "; " + CPrice + " --> " + NOPrice;
							arrString.add(s);
						}			
					}
					
					for(int i = arrString.size()-1; i >= 0; i--){
						System.out.println(arrString.get(i));
					}
					
					if (arrString.size() == 0){
						System.out.println("\n" + ticker + " does not have any splits. \n");
					}
					else{
						System.out.println("splits: " + arrString.size() + "\n");
					}
					arrString.removeAll(arrString);
					ticker = reader.getInput();
				}
				else { 
					System.out.println("\n" + ticker + " Does not exist in Database." + "\n");
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
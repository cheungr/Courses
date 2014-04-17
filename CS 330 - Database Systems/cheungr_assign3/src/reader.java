import java.io.*;



public class reader {

    //Gets input
	public static String getInput(){
		InputStreamReader istream = new InputStreamReader(System.in);
		BufferedReader bufRead = new BufferedReader(istream);
		String input = "";
		try {
			System.out.print("Enter a ticker symbol: ");
			input = bufRead.readLine();
		} catch (IOException err){
			System.out.println("Invalid INPUT! ERRRRRRRRRRRRRRRRRRRRRR");
		}
		return input;
	}

    //Verifies if the input is correct
	public static Boolean verify(String s){
		if (s.trim().length() == 0){
			return false;
		}
		else if (s.equals("")){
			return false;
		}
		else{
			return true;
		}
	}

}

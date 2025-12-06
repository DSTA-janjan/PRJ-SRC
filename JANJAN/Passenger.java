package JANJAN;
/**
 * The node i think
 */
public class Passenger {
	private String name;
	private String group;
	
	/**
	 * Instantiates Passenger with name and passenger type
	 * 
	 * 
	 * @param
	 *  name : name of the passenger <br
	 *  
	 * @param
	 *  type : 1 for VIP or 2 or Regular 
	 */
	public Passenger(String name, int type) {
		this.name = name;
		switch (type) {
		case 1: //VIP
			this.group = "VIP";
			break;
		case 2: //regular
			this.group = "Regular";
			break;
		}
	}
	
	public Passenger(String name, String group) {
		this.name = name;
		this.group = group;
	}
	
	public int getGroup() {
		if (group.equals("VIP"))
			return 1;
		else
			return 2;
	}
	
	public String getGroupString() {
		return group;
	}
	
	public String getName() {
		return name;
	}

}

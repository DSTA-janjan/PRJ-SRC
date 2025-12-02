package JANJAN;

import java.util.LinkedList;
import java.io.*;
import java.util.Scanner;

/**
 * que? <br>
 * basically the backend
 */
public class Queue {
	private LinkedList<Passenger> queue = new LinkedList<>();
	private FileHandler fh = new FileHandler();
	
	/**
	 * Inserting passenger to the queue
	 * 
	 * @param
	 *  name : Name of the passenger
	 *  
	 * @param
	 * 	type : VIP or regular | 1 or 2
	 */
	public int enqueue(String name, int type) {
		queue.add(new Passenger(name, type));
		System.out.println("Na queue na boss");
		try {
			fh.write(new Passenger(name, type));
		} 
        catch (IOException e) {
		}
		load();
		return 1;
	}
	
	/**
     * Displays all passenger, formatted
     */
	public int display() {
		if (isEmpty()) {
			System.out.println("Walay unud boss");
		}
		else {
            System.out.printf("%n%-12s%-15s|%-16s%-15s%n", "", "Regular", "", "VIP");
            String[] reg = new String[countRegular()];
            String[] vip = new String[countVIP()];
            
            int vp = 0, rg = 0;
            for (int i = 0; i < queue.size(); i++) {
                if (queue.get(i).getGroup() == 1) {
                    vip[vp] = queue.get(i).getName();
                    vp++;
                }
                else {
                    reg[rg] = queue.get(i).getName();
                    rg++;
                }
            }
            // System.out.printf("%d %d %d%n", reg.length, vp, rg);
            vp = rg = 0;
            for (int i = 0; i < queue.size(); i++, vp++, rg++) {
                String holdr = "", holdv = "";
                if (rg < reg.length)
                    holdr = reg[rg];
                if (vp < vip.length)
                    holdv = vip[vp];
                
                System.out.printf("%-27s|%-34s%n", holdr, holdv);
            }
		}
		return 1;
	}

    /**
     * Peeks elements
     * 
     * @param group : VIP or Regular | 1 or 2
     * @param where : front or back
     * @return
     */
    public String peek(int group, String where) {
        if (isEmpty())
            System.out.println("Walay unud boss");
        else {
            String answer = null;
            switch (group) { //1 = vip, 2 = regular
                case 1:
                    if (where.toLowerCase().equals("front")) {
                        for (Passenger enger : queue) {
                            if (enger.getGroup() == 1) {
                                answer = enger.getName();
                                break;
                            }
                        }
                    }
                    else if (where.toLowerCase().equals("rear")) {
                        int ctr = 1;
                        for (Passenger enger : queue) {
                            if (ctr == countVIP()) {
                                answer = enger.getName();
                                break;
                            }
                            else if (enger.getGroup() == 1)
                                ctr++;
                        }
                    }
                    else
                        System.out.println("Insert correctly, dumbass");
                    break;
                case 2:
                    if (where.toLowerCase().equals("front")) {
                        for (Passenger enger : queue) {
                            if (enger.getGroup() == 2) {
                                answer = enger.getName();
                                break;
                            }
                        }
                    }
                    else if (where.toLowerCase().equals("rear")) {
                        int ctr = 0;
                        System.out.println("regular: " + countRegular());
                        for (Passenger enger : queue) {
                            System.out.println("1." + enger.getName());
                            if (ctr < countRegular()) {
                                ctr++;
                            }
                            else {
                                System.out.println(ctr + " " + enger.getName());
                                answer = enger.getName();
                                break;
                            }
                        }
                    }
                    else
                        answer = "Insert correctly, dumbass";
                    break;
            }

            return answer;
        }
        return null;
    } 

    public void Board() {
        if(isEmpty()){
            System.out.println("No passengers to board.");
        }
        else {
            for(Passenger enger : queue) {
                if(enger.getGroup() == 1) {
                    System.out.println(enger.getName() + " has boarded the plane.");
                    queue.remove(enger);
                    return;
                }
            }
            for(Passenger enger : queue) {
                if(enger.getGroup() == 2) {
                    System.out.println(enger.getName() + " has boarded the plane.");
                    queue.remove(enger);
                    return;
                }
            }
        }
    }
	
    /**
     * Loads the data from the queue.txt file
     */
	public void load() {
		try {
			System.out.println("loaded");
			queue = fh.load();
		}
		catch (IOException e) {}
	}


	/**
     * Counts how many vips IN the linkedlist
     * 
     * @return
     */
	private int countVIP() {
        int vips = 0;
        try {
            if (queue.isEmpty()) {
                load();
            }
            
            for (Passenger senger : queue) {
                if (senger.getGroup() == 1)
                    vips++;
            }
        }
        catch (Exception e) {}
		
		return vips;
	}
	
    /**
     * Counts how many regulars IN the linkedlist
     * note: IN linkedlist, not IN the textfile
     * @return
     */
	private int countRegular() {
        int regular = 0;
        try {
            if (queue.isEmpty()) {
                load();
            }

            for (Passenger senger : queue) {
                if (senger.getGroup() == 2)
                    regular++;
            }
        }
        catch (Exception e) {}

		return regular;
	}
	
	public boolean isEmpty() {
		return queue.isEmpty();
	}
}

/**
 * The class for handling files <p>
 * All dealing with files MUST be in here <br>
 * for the sake of cleanliness
 */
class FileHandler {
	
	private File queue = new File("Queue.txt");
	
	public FileHandler() {
		
		try {
			if (!queue.exists()) {
				queue.createNewFile();
			}
		} catch (IOException e) {
			System.out.println("Could not create Queue.txt: " + e.getMessage());
		}
	}
	
	/**
	 * Writes things in the main text file.
	 *
	 * @param p : Passenger ADT
	 * @throws IOException
	 */
	public void write(Passenger p) throws IOException {
		// Create the file if it somehow doesn't exist yet
		if (!queue.exists()) {
			queue.createNewFile();
		}
		
		try (FileWriter fw = new FileWriter(queue, true)) {
			fw.write(String.format("%-30s | %-10s%n", p.getName(), p.getGroupString()));
		}
	}
	
	/**
	 * Loader for the starting up of the  <p>
	 * 
	 * #21//11 : As of now its just a way to preload the saved <br>
	 * queue from the previous execution. Could be expanded to <br>
	 * to something else in the future
	 * 
	 * @throws IOException
	 */
	public LinkedList<Passenger> load() throws IOException {
		LinkedList<Passenger> hold = new LinkedList<>();
		
		try (Scanner sc = new Scanner(new FileReader(queue))) {
			while (sc.hasNextLine()) {
				String[] holder = sc.nextLine().split("\\|");
				String name = holder[0].trim();
				String type = holder[1].trim();
				
				hold.add(new Passenger(name, type));
			}
		}
		
		return hold;
	}
}

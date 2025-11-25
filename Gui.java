package CCE105;


/**
 * Gui class for the porjet <br>
 * could say the front end part
 */
public class Gui {
	
	public static void main(String args[]) {
		Queue q = new Queue();

		q.load();
		// q.enqueue("John Christopher Damasco", 2);
		
		
		q.display();
		System.out.println(q.peek(1, "front"));
		System.out.println(q.peek(1, "rear"));
		System.out.println(q.peek(2, "front"));
		System.out.println(q.peek(2, "rear"));
	}
}

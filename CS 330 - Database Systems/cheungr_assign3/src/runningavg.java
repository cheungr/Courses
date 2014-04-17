public class runningavg {

    private int size;
    private double total = 0.0;
    private int index = 0;
    private double storage[];

    public runningavg(int size) {
        this.size = size;
        storage = new double[size];
        for (int i = 0; i < size; i++) storage[i] = 0.0;
    }

    public void add(double x) {
        total -= storage[index];
        storage[index] = x;
        total += x;
        if (++index == size) index = 0;
    }

    public double getAverage() {
        return total / size;
    }
}
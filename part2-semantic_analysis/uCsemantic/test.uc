int main () {
    int i, j, k = 0;
    i = 1;
    j = 2;
    
    while (3){
        i += j * k;
        k++;
    }

    assert i == 91;

    return 0;
}
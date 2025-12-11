#include <iostream>
#include <string>
#include <cctype>

using namespace std;

// -------------------------
//        MAPPER
// -------------------------
void run_mapper() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string line;
    while (getline(cin, line)) {
        string word;

        for (char ch : line) {
            if (isalnum((unsigned char)ch) || ch == '_') {
                // accumulate lowercase letters into word
                word.push_back(tolower((unsigned char)ch));
            } else {
                if (!word.empty()) {
                    cout << word << '\t' << 1 << '\n';
                    word.clear();
                }
            }
        }
        if (!word.empty()) {
            cout << word << '\t' << 1 << '\n';
        }
    }
}

// -------------------------
//        REDUCER
// -------------------------
void run_reducer() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string line, currentWord;
    long long currentCount = 0;
    bool first = true;

    while (getline(cin, line)) {
        if (line.empty()) continue;

        size_t tabPos = line.find('\t');
        if (tabPos == string::npos) continue;

        string word = line.substr(0, tabPos);
        long long count = stoll(line.substr(tabPos + 1));

        if (first) {
            currentWord = word;
            currentCount = count;
            first = false;
        } else if (word == currentWord) {
            currentCount += count;
        } else {
            cout << currentWord << '\t' << currentCount << '\n';
            currentWord = word;
            currentCount = count;
        }
    }

    if (!first) {
        cout << currentWord << '\t' << currentCount << '\n';
    }
}

// -------------------------
//        MAIN
// -------------------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage:\n"
             << "  ./wordcount map\n"
             << "  ./wordcount reduce\n";
        return 1;
    }

    string mode = argv[1];

    if (mode == "map") {
        run_mapper();
    } 
    else if (mode == "reduce") {
        run_reducer();
    } 
    else {
        cerr << "Unknown mode: " << mode << "\n"
             << "Use either 'map' or 'reduce'.\n";
        return 1;
    }

    return 0;
}

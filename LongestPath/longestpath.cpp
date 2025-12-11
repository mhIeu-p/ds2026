#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

using namespace std;

static const int LENGTH_WIDTH = 8; // up to 99,999,999 chars

// -------------------------
//           MAPPER
// -------------------------
void run_mapper() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string path;
    while (getline(cin, path)) {
        if (path.empty()) {
            continue; // ignore empty lines
        }

        size_t len = path.size();  // length in characters

        // zero-pad length so lexicographic sort == numeric sort
        ostringstream oss;
        oss << setw(LENGTH_WIDTH) << setfill('0') << len;
        string len_str = oss.str();

        cout << len_str << '\t' << path << '\n';
    }
}

// -------------------------
//           REDUCER
// -------------------------
void run_reducer() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string line;
    string max_len_str;
    vector<string> longest_paths;
    bool first = true;

    while (getline(cin, line)) {
        if (line.empty()) continue;

        size_t tab_pos = line.find('\t');
        if (tab_pos == string::npos) continue; // malformed

        string len_str = line.substr(0, tab_pos);
        string path    = line.substr(tab_pos + 1);

        if (first) {
            max_len_str = len_str;
            longest_paths.clear();
            longest_paths.push_back(path);
            first = false;
        } else {
            if (len_str > max_len_str) {
                // found strictly longer path length
                max_len_str = len_str;
                longest_paths.clear();
                longest_paths.push_back(path);
            } else if (len_str == max_len_str) {
                // another path with same max length
                longest_paths.push_back(path);
            }
            // if len_str < max_len_str: ignore
        }
    }

    if (first) {
        // no input at all
        return;
    }

    long long max_len = stoll(max_len_str);

    for (const auto& p : longest_paths) {
        cout << max_len << '\t' << p << '\n';
    }
}

// -------------------------
//            MAIN
// -------------------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage:\n"
             << "  ./longestpath map\n"
             << "  ./longestpath reduce\n";
        return 1;
    }

    string mode = argv[1];

    if (mode == "map") {
        run_mapper();
    } else if (mode == "reduce") {
        run_reducer();
    } else {
        cerr << "Unknown mode: " << mode << "\n"
             << "Use either 'map' or 'reduce'.\n";
        return 1;
    }

    return 0;
}

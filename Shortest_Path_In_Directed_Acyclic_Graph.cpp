#include <bits/stdc++.h>
using namespace std;

class Graph
{
public:
    // T.C. -> O(N + E)
    // S.C. -> O(N + E)
    // where N is the number of nodes in the graph
    // E is the number of edges in the graph
    unordered_map<int, list<pair<int, int>>> adj;

    void addEdge(int u, int v, int weight)
    {

        pair<int, int> p = {v, weight}; // neighbor v is stored as a pair of (node,weight)
        adj[u].push_back(p);
    }

    void printAdj()
    {
        cout << endl;
        for (auto i : adj)
        {
            cout << i.first << " -> ";
            for (auto j : i.second)
            {
                cout << "(" << j.first << "," << j.second << "), ";
            }
            cout << endl;
        }
    }

    void dfs(int node, unordered_map<int, bool> &visited, stack<int> &s)
    {
        visited[node] = true;
        for (auto i : adj[node])
        {
            if (!visited[i.first])
            {
                dfs(i.first, visited, s);
            }
        }
        s.push(node);
    }

    void getShortestPath(int src, vector<int> &dist, stack<int> &s)
    {

        dist[src] = 0; // As distance from source to source node is 0

        while (!s.empty())
        {
            int top = s.top();
            s.pop();

            if (dist[top] != INT_MAX)
            {
                for (auto i : adj[top])
                {
                    if (dist[top] + i.second < dist[i.first])
                    {
                        dist[i.first] = dist[top] + i.second;
                    }
                }
            }
        }
    }
};

int main()
{

    Graph g;

    g.addEdge(0, 1, 5);
    g.addEdge(0, 2, 3);
    g.addEdge(1, 2, 2);
    g.addEdge(1, 3, 6);
    g.addEdge(2, 3, 7);
    g.addEdge(2, 4, 4);
    g.addEdge(2, 5, 2);
    g.addEdge(3, 4, -1);
    g.addEdge(4, 5, -2);

    g.printAdj();

    int n = 6;
    // Topological Sort
    unordered_map<int, bool> visited;
    stack<int> s;

    for (int i = 0; i < n; i++)
    {
        if (!visited[i])
        {
            g.dfs(i, visited, s);
        }
    }

    int src = 1;
    vector<int> dist(n);
    for (int i = 0; i < n; i++)
    {
        dist[i] = INT_MAX;
    }

    g.getShortestPath(src, dist, s);
    cout << "\nShortest Path in this graph is: " << endl;
    for (int i = 0; i < dist.size(); i++)
    {
        cout << " " << dist[i] << " ";
    }
    cout << endl;

    return 0;
}

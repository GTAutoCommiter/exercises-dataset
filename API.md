# 🌐 Exercises Dataset Static REST API Documentation

This dataset provides a pre-generated, static RESTful JSON API optimized for hosting on **GitHub Pages** or serving via **jsDelivr CDN**. 

It breaks down the large dataset (`data/exercises.json`) into lightweight index lists, individual exercise details, categorized queries, and single-language localized files.

---

## 🚀 Base URLs

Replace `<username>` and `<repository>` with your GitHub details:

- **GitHub Pages Primary URL**:  
  `https://<username>.github.io/<repository>/`
- **jsDelivr CDN Global Acceleration URL** (Fast & Cached):  
  `https://cdn.jsdelivr.net/gh/<username>/<repository>@main/`

---

## 📡 API Endpoints Overview

| Endpoint Path | Description | Typical Size |
|---|---|---|
| `GET /api/v1/meta.json` | API metadata, dataset version, count statistics & endpoint directory | ~1 KB |
| `GET /api/v1/exercises.json` | Compact list of all 1,324 exercises (metadata only, no heavy instructions) | ~346 KB |
| `GET /api/v1/exercises/{id}.json` | Full details for a single exercise by ID (e.g. `0001.json`) with all 10 language instructions | ~11 KB |
| `GET /api/v1/categories.json` | Summary list of all categories with exercise counts | ~1.2 KB |
| `GET /api/v1/body-parts.json` | Summary list of all body parts with exercise counts | ~1.2 KB |
| `GET /api/v1/equipment.json` | Summary list of all 28 equipment types with exercise counts | ~3.6 KB |
| `GET /api/v1/targets.json` | Summary list of all target muscles with exercise counts | ~2.3 KB |
| `GET /api/v1/by-category/{category-slug}.json` | Exercises filtered by category (e.g. `waist.json`, `chest.json`) | Varies |
| `GET /api/v1/by-body-part/{body-part-slug}.json` | Exercises filtered by body part (e.g. `upper-arms.json`) | Varies |
| `GET /api/v1/by-equipment/{equipment-slug}.json` | Exercises filtered by equipment (e.g. `body-weight.json`, `dumbbell.json`) | Varies |
| `GET /api/v1/by-target/{target-slug}.json` | Exercises filtered by target muscle (e.g. `abs.json`, `biceps.json`) | Varies |
| `GET /api/v1/lang/{lang}.json` | Full dataset localized to a single language (`en`, `zh`, `es`, `fr`, `it`, `tr`, `ru`, `hi`, `pl`, `ko`) | ~1.2 MB |

---

## 💻 Backend Integration Examples

GitHub Pages automatically serves all static files with CORS headers (`Access-Control-Allow-Origin: *`). Any backend framework can consume these endpoints directly.

### 1. Python (`requests` / `httpx`)

```python
import requests

BASE_URL = "https://<username>.github.io/<repository>/api/v1"

# 1. Fetch metadata
meta = requests.get(f"{BASE_URL}/meta.json").json()
print(f"Total exercises: {meta['total_exercises']}")

# 2. Get exercises localized in Chinese
zh_exercises = requests.get(f"{BASE_URL}/lang/zh.json").json()
print("First exercise:", zh_exercises[0]['name'], zh_exercises[0]['instruction'])

# 3. Get single exercise details (e.g., 0001)
ex_0001 = requests.get(f"{BASE_URL}/exercises/0001.json").json()
print("Instructions (EN):", ex_0001['instructions']['en'])
```

### 2. Node.js / TypeScript (`fetch` / `axios`)

```typescript
const BASE_URL = 'https://<username>.github.io/<repository>/api/v1';

async function fetchExercises() {
  // Fetch lightweight exercise index
  const res = await fetch(`${BASE_URL}/exercises.json`);
  const exercises = await res.json();
  console.log(`Loaded ${exercises.length} exercises.`);

  // Fetch bodyweight exercises only
  const bwRes = await fetch(`${BASE_URL}/by-equipment/body-weight.json`);
  const bodyweightExercises = await bwRes.json();
  console.log(`Found ${bodyweightExercises.length} bodyweight exercises.`);
}

fetchExercises();
```

### 3. Go (`net/http`)

```go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type ExerciseSummary struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Category  string `json:"category"`
	Equipment string `json:"equipment"`
	Target    string `json:"target"`
}

func main() {
	url := "https://<username>.github.io/<repository>/api/v1/exercises.json"
	resp, err := http.Get(url)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	var exercises []ExerciseSummary
	json.NewDecoder(resp.Body).Decode(&exercises)
	fmt.Printf("Fetched %d exercises via Go\n", len(exercises))
}
```

### 4. Java (`java.net.http.HttpClient`)

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ApiClient {
    public static void main(String[] args) throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://<username>.github.io/<repository>/api/v1/meta.json"))
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("Meta response:\n" + response.body());
    }
}
```

### 5. cURL

```bash
# Fetch single exercise
curl -s https://<username>.github.io/<repository>/api/v1/exercises/0001.json

# Fetch Chinese localized dataset via jsDelivr CDN
curl -s https://cdn.jsdelivr.net/gh/<username>/<repository>@main/api/v1/lang/zh.json
```

---

## ⚡ Performance & Caching Recommendations

1. **Use `api/v1/exercises.json` for Search & Filters**:  
   Do not download the 17.3MB raw file or full exercise details if your backend only needs titles, categories, and images for list/grid UI.
2. **CDN Acceleration**:  
   For production backends with high traffic, use `https://cdn.jsdelivr.net/gh/<user>/<repo>@main/` for edge caching and faster response times globally.
3. **Backend Memory Caching**:  
   Since fitness exercise data changes infrequently, backends should cache responses (e.g. in Redis or memory for 24h) and use `api/v1/meta.json` to check `last_updated` before invalidating cache.

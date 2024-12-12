import requests


def search_names(names):
    url = "https://iitd.ac.in/includes/search.php"
    payload = {"names": names}

    try:
        response = requests.post(url, data=payload, verify=False)
        print("Response text:", response.text)  # Debug the raw response

        if response.status_code == 200:
            try:
                json_data = response.json()  # Attempt to parse JSON
                return json_data if json_data else {"error": "Empty JSON response"}
            except requests.exceptions.JSONDecodeError:
                print("Error parsing JSON")
                return {"error": "Invalid JSON format"}
        else:
            print(f"Request failed with status code {response.status_code}")
            return {"error": f"Request failed with status code {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    names = [
    "SS Murthy",
    "Anandarup Das",
    "Rahul Agarwal",
    "Utkarsh Sharma",
    "Ankit Singhal",
    "Gaurav Modi",
    "Pavitra Shukl",
    "Dhiman Das",
    "Aswin Dilip Kumar",
    "DEEPU VIJAY M",
    "Hina Parveen",
    "NIBEDITA PARIDA",
    "SUDIP BHATTACHARYYA",
    "Gourav Kumar Mishra",
    "Akankshi Trivedi",
    "Shrikant Misal",
    "Sukrashis Sarkar",
    "Subir Karmakar",
    "Adnan Khan",
    "Mohammad Saleh Khan",
    "Suvom Roy",
    "Ambuj Sharma",
    "Muhammad Zarkab Farooqi",
    "Gurmeet Singh",
    "Atul Sharma",
    "Niteesh Shanbog",
    "Purusharth Semwal",
    "Smita Mohanty",
    "Cheshta Jain",
    "Abhrodip Chaudhury",
    "Akshay Kumar Bhyri",
    "Akash Kedia",
    "Uzmah Javed",
    "Subhadip Sadhukhan",
    "Abhishek Abhinav Nanda",
    "Tanay Mistry",
    "Shashank Panikkar",
    "Sharvendra Kumar Omre",
    "Gautam Karthik V",
    "Tanusree"
  ]

    base_url = "https://example.com/people"  # Replace with the actual base URL
    result = search_names(names)

    for name, page in result.items():
        print(f"{name}: {page}")

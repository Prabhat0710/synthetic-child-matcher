# 🗺️ Care Map 

> **A Data-Driven Matching Platform for Foster Care and Adoption Agencies**

Care Map (formerly Synthetic Child Matcher) is an interactive, intelligent web application designed to bridge the gap between children requiring specific support and the foster/adoptive families capable of providing it. 

Built for agency administrators and prospective parents, the platform uses a dynamic questionnaire to evaluate a family's capacity across five core domains—**Medical, Behavioral, Educational, Emotional,** and **Physical**—and mathematically pairs them with children based on minimizing capability gaps.

---

## ✨ Key Features

### 👨‍👩‍👧 For Prospective Parents
* **Interactive Capacity Questionnaire:** A comprehensive 30-question intake form that translates real-world scenarios into quantitative capacity metrics.
* **Live Progress Tracking:** Visual feedback as parents fill out the questionnaire. State-persistence ensures answers aren't lost between sessions.
* **Review Invitations:** A clean inbox where parents can review child profiles sent by the agency, complete with interactive **Accept / Decline** confirmation modals.

### 🏢 For Agency Administrators
* **System-Wide Dashboard:** Track total children, approved families, and view a visual "Gap Analysis" chart showing average unmet needs across the system.
* **AI Capacity Assessments:** Instantly generated text summaries of a family's **Strong Points**, **Weak Points**, and **Moderate Areas** based purely on their questionnaire data.
* **Mathematical Matching Engine:** Select any child in the system to view a sorted, color-coded dataframe ranking every family's compatibility score (0-100%).
* **Invitation Workflow:** Send match invitations directly to a family's portal with a single click, and track whether the invite is `pending`, `accepted`, or `declined` in real-time.
* **In-App Data Management:** Upload new `synthetic_children.csv` databases directly from the sidebar without touching the codebase.

---

## 🛠️ Technical Architecture

Care Map is built entirely in **Python**, utilizing **Streamlit** for the frontend, **Pandas** / **Scikit-Learn** for data processing, and **SQLite** for relational record keeping.

### Core Modules
* `app/main.py`: The entry point. Handles session-state routing (Home, Login, App) and sidebar rendering.
* `app/ui/`: Contains the isolated views for `parent_view.py` and `admin_analysis.py`.
* `app/backend/contracts.py`: The strict API layer. Separates frontend UI logic from the backend database operations.
* `app/processing/`: The data engine. Calculates the normalized needs of the child vs. the capacities of the family (`preprocess.py`), applies cosine similarity for scoring (`matcher.py`), and handles CSV loading (`data_loader.py`).
* `app/db/database.py`: Manages the SQLite database (`matches.db`) tracking invitations, match statuses, and engine barriers.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prabhat0710/synthetic-child-matcher.git
   cd synthetic-child-matcher
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app/main.py
   ```

---

## 📖 Usage Guide & Testing Flow

To evaluate the platform, follow this testing loop:

1. **Log in as Admin:**
   * Username: `admin` | Password: `admin`
   * Go to the **Data Management** sidebar and upload a dummy children CSV (if none exists).
   * Notice that the dashboards are empty if no parents have completed their profiles.
2. **Log in as a Parent:**
   * Create a new user (or log into an existing one).
   * Complete the 30-question survey. Observe the live progress bar.
   * Click **Submit & Save Profile**.
3. **Send an Invitation (Admin):**
   * Log back in as `admin`.
   * Go to the **Children (Matches)** tab. Select a child to see how the parent you just created scores.
   * Click **Send Invite**.
4. **Accept/Decline (Parent):**
   * Log back into the parent account.
   * Check the **Invitations** tab. Click **Accept**, click **Yes, confirm** on the popup.
5. **Track Status (Admin):**
   * Log into `admin`, scroll to the bottom of the **Dashboard Overview** tab, and observe the Invitation Status Tracking table change to green (`accepted`).

---

## 🔮 Future Roadmap
* Integration with the **Google Gemini API** to generate rich, narrative explanations detailing *why* a specific family is a great fit for a child.
* Email notifications triggered upon invitation status updates.
* Multi-agency tenanting architecture for nationwide scaling.
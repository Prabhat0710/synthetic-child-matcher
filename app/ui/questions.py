# Questionnaire definition for Parent Matching

QUESTIONNAIRE = {
    "1. Family & Household": [
        {"id": "q1", "text": "Q1. How many adults currently live in your household?", "options": ["1", "2", "3", "4 or more"]},
        {"id": "q2", "text": "Q2. How many children currently live in your household?", "options": ["0", "1", "2", "3", "4 or more"]},
        {"id": "q3", "text": "Q3. What age groups are the children currently in your household?", "options": ["Infant / Toddler", "School age", "Teenager", "Multiple age groups", "Not applicable"]},
        {"id": "q4", "text": "Q4. Who would be the primary day-to-day caregiver for the child?", "options": ["One parent", "Both parents", "Parent + another household member", "Shared caregiving arrangement", "Other"]},
        {"id": "q5", "text": "Q5. How much support could you realistically receive from extended family or trusted friends if needed?", "options": ["Very little", "Some", "Moderate", "A lot", "Not applicable"]}
    ],
    "2. Time & Daily Care": [
        {"id": "q6", "text": "Q6. How much time could the household realistically make available for the child's daily care and support?", "options": ["Less than 1 hour/day", "1–3 hours", "3–5 hours", "5–8 hours", "Most of the day"]},
        {"id": "q7", "text": "Q7. How flexible is the household's daily schedule when routines or appointments change?", "options": ["Not very flexible", "Slightly flexible", "Moderately flexible", "Very flexible", "Highly flexible"]},
        {"id": "q8", "text": "Q8. How comfortable are you with everyday care such as meals, dressing, bathing, hygiene, and routines?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"]},
        {"id": "q9", "text": "Q9. How comfortable are you with maintaining a consistent daily routine?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"]},
        {"id": "q10", "text": "Q10. How comfortable are you with attending appointments, school meetings, activities, or other regular commitments?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"]}
    ],
    "3. Health & Medical Support": [
        {"id": "q11", "text": "Q11. How comfortable are you with managing healthcare appointments and communicating with healthcare professionals?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "medical_capacity"},
        {"id": "q12", "text": "Q12. How comfortable are you with following professional healthcare plans, such as medication schedules, dietary instructions, exercises, or follow-ups?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "medical_capacity"},
        {"id": "q13", "text": "Q13. What level of healthcare-related support could your household realistically provide?", "options": ["Basic appointment/support coordination", "Regular care following professional guidance", "Frequent hands-on support", "Extensive support with significant daily involvement", "Unsure"], "maps_to": "medical_capacity"},
        {"id": "q14", "text": "Q14. Do you or another household member have professional training or experience in healthcare, caregiving, therapy, nursing, or a related field?", "options": ["No", "Yes — limited experience", "Yes — substantial experience", "Prefer to describe in Q30"], "maps_to": "medical_capacity"}
    ],
    "4. Learning, Development & Communication": [
        {"id": "q15", "text": "Q15. How comfortable are you with supporting a child's learning or education at home?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "educational_capacity"},
        {"id": "q16", "text": "Q16. How comfortable are you with working with teachers, counselors, therapists, or other professionals?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "educational_capacity"},
        {"id": "q17", "text": "Q17. How comfortable are you with adapting communication methods when needed, such as visual aids, gestures, communication devices, or other approaches?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "educational_capacity"},
        {"id": "q18", "text": "Q18. How willing is your household to learn new skills, routines, or support techniques when recommended by qualified professionals?", "options": ["Not willing", "Slightly willing", "Moderately willing", "Very willing", "Fully willing"], "maps_to": "educational_capacity"}
    ],
    "5. Emotional & Behavioral Support": [
        {"id": "q19", "text": "Q19. How comfortable are you with providing patience, reassurance, and support when a child is stressed, frustrated, worried, or afraid?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "emotional_capacity"},
        {"id": "q20", "text": "Q20. How comfortable are you with responding calmly and consistently when a child is experiencing emotional or behavioral difficulties?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "behavioral_capacity"},
        {"id": "q21", "text": "Q21. How comfortable are you with following guidance from qualified professionals for emotional, behavioral, or developmental support?", "options": ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Very comfortable", "Fully comfortable"], "maps_to": "behavioral_capacity"},
        {"id": "q22", "text": "Q22. Which best describes your household environment?", "options": ["Very quiet and predictable", "Mostly calm and predictable", "Moderately active", "Quite active", "Highly active or frequently changing"], "maps_to": "emotional_capacity"}
    ],
    "6. Physical Environment & Accessibility": [
        {"id": "q23", "text": "Q23. What type of living environment does the household currently have?", "options": ["Apartment", "House", "Shared accommodation", "Other"]},
        {"id": "q24", "text": "Q24. How suitable is your home for a child who may have difficulty with stairs, walking, or physical movement?", "options": ["Not suitable", "Somewhat suitable", "Moderately suitable", "Very suitable", "Fully accessible"], "maps_to": "physical_capacity"},
        {"id": "q25", "text": "Q25. Which accessibility or safety features are currently available in your home?", "options": ["Stairs", "Elevator", "Ground-floor access", "Accessible bathroom", "Extra space for equipment or movement", "Outdoor space", "Limited accessibility", "None", "Other"], "maps_to": "physical_capacity"},
        {"id": "q26", "text": "Q26. How able would your household be to make reasonable changes to the home if needed for safety or accessibility?", "options": ["Not able", "Slightly able", "Moderately able", "Very able", "Highly able"], "maps_to": "physical_capacity"}
    ],
    "7. Preferences, Expectations & Support": [
        {"id": "q27", "text": "Q27. Which age group(s) does your household feel best prepared to support?", "options": ["Infant / Toddler", "School age", "Teenager", "Multiple age groups", "No strong preference"]},
        {"id": "q28", "text": "Q28. Which types of support is your household prepared to provide? (Select all that apply.)", "options": ["Daily routines", "Educational support", "Emotional support", "Behavioral support", "Healthcare coordination", "Physical support", "Communication support", "Social or recreational activities", "Willing to learn additional support skills"], "type": "multiselect"},
        {"id": "q29", "text": "Q29. Are there circumstances that could make consistent care difficult for your household?", "options": ["Work schedule", "Travel", "Caregiver availability", "Housing limitations", "Financial limitations", "Transportation", "Existing caregiving responsibilities", "Limited nearby support", "None", "Other"], "type": "multiselect"},
        {"id": "q30", "text": "Q30. Is there anything else the matching team should know about your household, capabilities, environment, or circumstances?", "options": [], "type": "text"}
    ]
}

def score_answer(ans: str) -> int:
    """Map natural language answers to 1-10 capacity scores."""
    if not isinstance(ans, str): return 5
    ans = ans.lower()
    
    if "not comfortable" in ans or "not able" in ans or "not suitable" in ans or "not willing" in ans or "no" == ans or "very little" in ans: 
        return 1
    if "slightly" in ans or "some" in ans or "somewhat" in ans or "limited" in ans or "basic" in ans: 
        return 3
    if "moderately" in ans or "moderate" in ans or "regular" in ans: 
        return 5
    if "very" in ans or "a lot" in ans or "quite" in ans or "frequent" in ans or "substantial" in ans: 
        return 7
    if "fully" in ans or "highly" in ans or "most" in ans or "extensive" in ans: 
        return 10
        
    return 5 # Neutral fallback for other answers

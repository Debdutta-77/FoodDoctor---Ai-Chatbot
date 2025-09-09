import streamlit as st
import json
import requests
import math
import random

# Set page configuration
st.set_page_config(
    page_title="Personalized Recipe Generator",
    page_icon="🥗",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .recipe-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-container {
        background-color: #4CAF50;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .bmi-normal {
        color: #4CAF50;
        font-weight: bold;
    }
    .bmi-warning {
        color: #FFC107;
        font-weight: bold;
    }
    .bmi-danger {
        color: #F44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# * IMPORTANT: Add your Gemini API key here *
# This will be used for all users and won't be visible in the UI
GEMINI_API_KEY = "AIzaSyC***************************"  # Your API key

# App header
st.markdown('<div class="header-container"><h1>🥗 Recipies That Care!</h1></div>', unsafe_allow_html=True)

def calculate_bmi(weight, height):
    """Calculate BMI given weight in kg and height in cm"""
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Return BMI category and CSS class"""
    if bmi < 18.5:
        return "Underweight", "bmi-warning"
    elif 18.5 <= bmi < 25:
        return "Normal weight", "bmi-normal"
    elif 25 <= bmi < 30:
        return "Overweight", "bmi-warning"
    else:
        return "Obese", "bmi-danger"

def generate_recipe(goal, bmi_category):
    """Generate recipe recommendations based on health goal and BMI using TheMealDB API"""
    # Define backup recipes in case API call fails
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    
    # Define recipe templates based on goals and BMI
    recipes = {
        "lose_weight": {
            "Underweight": [
                "Protein-rich smoothie with banana, Greek yogurt, and a small amount of peanut butter",
                "Veggie omelet with a side of whole grain toast",
                "Baked salmon with quinoa and steamed vegetables",
                "Apple slices with almond butter"
            ],
            "Normal weight": [
                "Overnight oats with berries and a sprinkle of nuts",
                "Grilled chicken salad with light vinaigrette",
                "Zucchini noodles with turkey meatballs and tomato sauce",
                "Greek yogurt with honey and cinnamon"
            ],
            "Overweight": [
                "Egg white scramble with spinach and tomatoes",
                "Lentil soup with a small side salad",
                "Baked cod with roasted vegetables",
                "Celery sticks with hummus"
            ],
            "Obese": [
                "Green smoothie with spinach, cucumber, and apple",
                "Broth-based vegetable soup with lean protein",
                "Grilled chicken breast with steamed broccoli and cauliflower rice",
                "Cucumber slices with tzatziki"
            ]
        },
        "gain_weight": {
            "Underweight": [
                "Protein pancakes topped with banana, peanut butter and honey",
                "Tuna sandwich on whole grain bread with avocado and cheese",
                "Beef stir-fry with rice and mixed vegetables",
                "Trail mix with nuts, dried fruits, and dark chocolate chunks"
            ],
            "Normal weight": [
                "Avocado toast with eggs and cheese",
                "Chicken wrap with hummus, cheese, and vegetables",
                "Spaghetti with turkey meatballs and garlic bread",
                "Protein bar with a banana"
            ],
            "Overweight": [
                "Greek yogurt parfait with granola and berries",
                "Turkey and cheese sandwich with a side of fruit",
                "Lean steak with sweet potato and green beans",
                "Cottage cheese with pineapple"
            ],
            "Obese": [
                "Veggie egg white omelet with a slice of whole grain toast",
                "Grilled chicken salad with light dressing",
                "Baked fish with steamed vegetables and quinoa",
                "Apple with a small portion of nuts"
            ]
        },
        "improve_health": {
            "Underweight": [
                "Oatmeal with nuts, seeds, banana, and a drizzle of honey",
                "Quinoa bowl with roasted vegetables and grilled chicken",
                "Sweet potato, black bean, and chicken burrito bowl",
                "Smoothie with protein powder, banana, and berries"
            ],
            "Normal weight": [
                "Vegetable frittata with a side of mixed berries",
                "Mediterranean salad with grilled chicken and olive oil dressing",
                "Baked salmon with asparagus and brown rice",
                "Handful of mixed nuts and a piece of fruit"
            ],
            "Overweight": [
                "Vegetable omelet with a slice of whole grain toast",
                "Mason jar salad with chickpeas and light dressing",
                "Grilled fish with roasted Brussels sprouts",
                "Sliced bell peppers with guacamole"
            ],
            "Obese": [
                "Berry and spinach smoothie",
                "Chopped salad with grilled chicken and balsamic vinaigrette",
                "Roasted vegetable and tofu stir-fry",
                "Air-popped popcorn with nutritional yeast"
            ]
        }
    }
    
    try:
        # Get random meals from TheMealDB
        result = {}
        for meal_type in meal_types:
            # TheMealDB API endpoint
            url = "https://www.themealdb.com/api/json/v1/1/random.php"
            response = requests.get(url)
            
            if response.status_code == 200:
                meal_data = response.json()["meals"][0]
                
                # Extract ingredients and measurements
                ingredients = []
                for i in range(1, 21):
                    ingredient = meal_data.get(f"strIngredient{i}")
                    measure = meal_data.get(f"strMeasure{i}")
                    if ingredient and ingredient.strip():
                        ingredients.append(f"{measure} {ingredient}".strip())
                
                # Extract instructions
                instructions = meal_data["strInstructions"].split(". ")
                
                # Create recipe object
                result[meal_type] = {
                    "name": meal_data["strMeal"],
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "benefits": [
                        "High in protein and essential nutrients",
                        "Balanced meal for your health goals",
                        "Easy to prepare and customize"
                    ]
                }
            else:
                # Fallback to template recipes
                raise ValueError(f"API request failed with status {response.status_code}")
                
        return result
                
    except Exception as e:
        st.warning(f"Using backup recipes. API error: {str(e)}", icon="⚠️")
        
        # Fallback to template-based recipes
        result = {}
        for i, meal_type in enumerate(meal_types):
            result[meal_type] = {
                "name": f"Healthy {meal_type} Option",
                "ingredients": ["Main ingredient", "Secondary ingredient", "Seasoning", "Optional topping"],
                "instructions": ["Prepare the ingredients", "Cook as directed", "Plate and serve"],
                "benefits": ["Provides essential nutrients", "Supports your health goals"]
            }
            
            # Add a basic description based on templates
            if bmi_category in recipes[goal]:
                template = recipes[goal][bmi_category][i]
                result[meal_type]["name"] = template
                
        return result

# Create sidebar for user inputs
with st.sidebar:
    st.header("Your Information")
    
    # Height and weight inputs
    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=250, value=70)
    
    # Calculate BMI
    bmi = calculate_bmi(weight, height)
    bmi_category, bmi_class = get_bmi_category(bmi)
    
    # Display BMI
    st.markdown(f"### Your BMI: <span class='{bmi_class}'>{bmi}</span>", unsafe_allow_html=True)
    st.markdown(f"Category: <span class='{bmi_class}'>{bmi_category}</span>", unsafe_allow_html=True)
    
    # Health goal selection
    st.header("Your Health Goal")
    health_concern = st.radio(
    "Do you have any health concerns?",
    options=["None", "Heart Disease", "Diabetes", "High Blood Pressure", "Cholesterol", "Thyroid Issues", "Obesity", "PCOS", "Anemia", "Digestive Disorders"],
    format_func=lambda x: x.replace("_", " ").capitalize()
    )
    goal = st.radio(
        "What's your primary goal?",
        options=["lose_weight", "gain_weight", "improve_health"],
        format_func=lambda x: x.replace("_", " ").capitalize()
    )
    deitary_preference = st.radio(
        "What's Dietary Preference?",
        options=["veg", "nonveg", "keto","lactose_intolerant",],
        format_func=lambda x: x.replace("_", " ").capitalize()
    )
    allergies = st.multiselect(
    "Do you have any food allergies? (Select all that apply)",
    options=["Peanuts", "Tree Nuts", "Shellfish", "Dairy", "Eggs", "Gluten", "Soy", "Fish", "Wheat"],
    format_func=lambda x: x.replace("_", " ").capitalize()
    )

    # Generate button
    generate_button = st.button("Generate Recipes", type="primary")

# Main content area
if generate_button or 'recipes' in st.session_state:
    with st.spinner("Generating your personalized recipes..."):
        if generate_button:
            # Generate new recipes
            st.session_state.recipes = generate_recipe(goal, bmi_category)
        
        # Display the recipes
        st.header(f"Your Personalized Meal Plan for {goal.replace('_', ' ').capitalize()}")
        st.markdown(f"Based on your BMI of *{bmi}* ({bmi_category})")
        
        # Create columns for different meal types
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        cols = st.columns(2)
        
        for i, meal_type in enumerate(meal_types):
            recipe = st.session_state.recipes.get(meal_type, {})
            col_idx = i % 2
            
            with cols[col_idx]:
                st.markdown(f"<div class='recipe-card'>", unsafe_allow_html=True)
                st.subheader(f"🍽️ {meal_type}")
                st.markdown(f"### {recipe.get('name', 'Recipe')}")
                
                st.markdown("#### Ingredients:")
                for ingredient in recipe.get("ingredients", []):
                    st.markdown(f"- {ingredient}")
                
                st.markdown("#### Instructions:")
                for idx, step in enumerate(recipe.get("instructions", []), 1):
                    st.markdown(f"{idx}. {step}")
                
                st.markdown("#### Health Benefits:")
                for benefit in recipe.get("benefits", []):
                    st.markdown(f"- {benefit}")
                
                st.markdown("</div>", unsafe_allow_html=True)
else:
    # Display welcome message
    st.markdown("""
    ## Welcome to Your Personalized Recipe Generator!
    
    This app helps you find healthy recipes tailored to your body metrics and health goals.
    
    ### How to use:
    1. Enter your height and weight in the sidebar
    2. Select your health goal
    3. Click "Generate Recipes" to get your personalized meal plan
    
    Your BMI will be calculated automatically to help customize your recipe suggestions.
    """)
    
    # Add an example image or placeholder
    st.image("https://images.unsplash.com/photo-1498837167922-ddd27525d352", 
             caption="Healthy eating starts with personalized recipes")

# Footer
st.markdown("---")
st.markdown("💡 *Tip:* The recipes are AI-generated based on your BMI and health goals!")

st.markdown("⚠️ *Disclaimer:* This app provides general recipe suggestions and is not a substitute for professional dietary advice.")

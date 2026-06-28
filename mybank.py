import streamlit as st
import json
import random
import string
import pandas as pd  # Used to display the accounts list in a clean table grid
from pathlib import Path

DATABASE = 'bank_data.json'

if not Path(DATABASE).exists():
    with open(DATABASE, 'w') as fs:
        fs.write(json.dumps([]))

def load_data():
    with open(DATABASE, 'r') as fs:
        content = fs.read().strip()
        return json.loads(content) if content else []

def save_data(data):
    with open(DATABASE, 'w') as fs:
        fs.write(json.dumps(data, indent=4))

def generate_account_no():
    alpha = random.choices(string.ascii_letters, k=3)
    num = random.choices(string.digits, k=3)
    spchar = random.choices("!@#$%^&*", k=1)
    id_list = alpha + num + spchar
    random.shuffle(id_list)
    return "".join(id_list)

# --- WEB UI DESIGN SETUP ---
st.set_page_config(page_title="Mudra Smart Bank", page_icon="🏦", layout="centered")
st.title("⚡ मुद्रा स्मार्ट बैंक (Mudra Smart Bank)")
st.markdown("---")

st.sidebar.markdown("## 🖥️ Navigation Portal")
menu = ["Home Dashboard", "Open New Account", "Deposit Vault", "Secure Withdrawal", "Account Statement", "All Registered Accounts", "Modify Profile Details", "Terminate Account"]
choice = st.sidebar.selectbox("Choose Operation", menu)

data = load_data()

# --- 1. HOME PAGE ---
if choice == "Home Dashboard":
    st.markdown("### 📊 System Overview")
    st.info("Welcome back to your central banking command. Use the control portal on the left sidebar to orchestrate transactions.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Server Vault Status", value="🟢 ONLINE")
    with col2:
        st.metric(label="Total Registrations", value=len(data))

# --- 2. CREATE ACCOUNT ---
elif choice == "Open New Account":
    st.markdown("### 📝 Digital Registration Form")
    with st.container(border=True):
        name = st.text_input("👤 Full Name")
        age = st.number_input("📅 Age Verification", min_value=0, value=18)
        email = st.text_input("📧 Email Registry")
        pin = st.text_input("🔐 Secure 4-Digit PIN", type="password", max_chars=4)

        if st.button("🚀 Authorize & Register"):
            if age < 18 or len(pin) != 4 or not pin.isdigit():
                st.error("❌ Registry Denied: Invalid age criteria (Must be 18+) or PIN structure (Must be 4 digits).")
            else:
                new_acc = generate_account_no()
                data.append({"name": name, "age": int(age), "email": email, "pin": int(pin), "AccountNo.": new_acc, "Balance": 0})
                save_data(data)
                st.success("🎉 Ledger updated! Account initialized successfully.")
                st.info(f"🔑 **Generated Account ID:** {new_acc} (Safeguard this code securely)")

# --- 3. ALL REGISTERED ACCOUNTS ---
elif choice == "All Registered Accounts":
    st.markdown("### 🗃️ Master Ledger: All Registered Accounts")
    if len(data) == 0:
        st.warning("No accounts have been registered in the bank directory yet.")
    else:
        st.info(f"Currently, there are {len(data)} active accounts stored on the server.")
        
        # Convert dictionary data to a clean DataFrame table
        df = pd.DataFrame(data)
        
        # Security masking: Hide the original PIN values for data privacy
        if 'pin' in df.columns:
            df['pin'] = "****"
            
        # Standardizing the column headers to clean English names
        df.columns = ["Name", "Age", "Email ID", "PIN (Hidden)", "Account Number", "Current Balance (₹)"]
        
        # Render the secure table grid inside the app
        st.dataframe(df, use_container_width=True)

# --- CORE SYSTEM AUTHORIZATION (For remaining operational features) ---
else:
    st.markdown(f"### 🛡️ Secure Authorization Required")
    with st.container(border=True):
        acc_input = st.text_input("💳 Account Number ID")
        pin_input = st.text_input("🔑 Authorization PIN", type="password", max_chars=4)
    
    current_user = None
    if acc_input and pin_input.isdigit():
        for user in data:
            if user['AccountNo.'] == acc_input and user['pin'] == int(pin_input):
                current_user = user
                break

    if acc_input and pin_input and not current_user:
        st.error("🔒 Security Alert: Credentials mismatched. Access denied.")

    # --- 4. DEPOSIT ---
    if choice == "Deposit Vault" and current_user:
        st.markdown("### 📥 Deposit Processing")
        st.write(f"**Verified User:** `{current_user['name']}`")
        amount = st.number_input("Liquidity Amount to Inject (Max ₹10,000)", min_value=1, max_value=10000)
        if st.button("💳 Commit Deposit"):
            current_user['Balance'] += amount
            save_data(data)
            st.success(f"✅ Assets added! Updated Reserve: **₹{current_user['Balance']}**")

    # --- 5. WITHDRAW ---
    elif choice == "Secure Withdrawal" and current_user:
        st.markdown("### 📤 Cash Dispensation")
        st.write(f"**Verified User:** `{current_user['name']}`")
        st.write(f"**Available Ledger Balance:** ₹{current_user['Balance']}")
        amount = st.number_input("Dispensation Request Amount", min_value=1)
        if st.button("🏧 Dispatch Funds"):
            if current_user['Balance'] < amount:
                st.error("⚠️ Transaction Failed: Insufficient vault reserves.")
            else:
                current_user['Balance'] -= amount
                save_data(data)
                st.success(f"💸 Assets dispatched! Remaining Capital: **₹{current_user['Balance']}**")

    # --- 6. ACCOUNT DETAILS ---
    elif choice == "Account Statement" and current_user:
        st.markdown("### 📜 System Matrix Logs")
        st.write(f"**Account Master Record:**")
        st.json(current_user)

    # --- 7. UPDATE PROFILE ---
    elif choice == "Modify Profile Details" and current_user:
        st.markdown("### ⚙️ Adjust Registry Parameters")
        st.warning("Locked Fields: Age, Account ID, and Ledger Balance cannot be compromised.")
        new_name = st.text_input("Modify Name Parameter", value=current_user['name'])
        new_email = st.text_input("Modify Email Parameter", value=current_user['email'])
        new_pin = st.text_input("Overwrite 4-Digit PIN (Blank to ignore)", type="password", max_chars=4)
        
        if st.button("💾 Apply Configuration Updates"):
            current_user['name'] = new_name
            current_user['email'] = new_email
            if new_pin.strip():
                if len(new_pin) == 4 and new_pin.isdigit():
                    current_user['pin'] = int(new_pin)
                else:
                    st.error("❌ Update Rejected: Weak PIN specification.")
            save_data(data)
            st.success("✨ System profile adjustments synchronized successfully.")

    # --- 8. DELETE ACCOUNT ---
    elif choice == "Terminate Account" and current_user:
        st.markdown("### 🚨 Danger Zone")
        st.error(f"Critical Action: Are you absolutely certain you want to purge the account for `{current_user['name']}`?")
        if st.button("💀 Confirm Absolute Deletion"):
            data.remove(current_user)
            save_data(data)
            st.success("💥 Account logs completely expunged from the master directory.")
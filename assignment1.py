import streamlit as st

# App title
st.title("The Identity Echo Interface")

# Instructions for the user
st.write("Enter your name and message below, then click the Transmit button.")

# Get user input
user_name = st.text_input("Name")
user_message = st.text_input("Message")

# Run only when the button is clicked
if st.button("Transmit"):

    # Check if the name is empty
    if user_name == "":
        st.error("Please provide your name.")

    # Check if the message is empty
    elif user_message == "":
        st.warning("Please type a message to transmit.")

    # Display success message if both inputs are provided
    else:
        st.success(
            f"Transmission successful! Greetings, {user_name}. "
            f"We received your message: {user_message}"
        )

        # Calculate estimated tokens
        character_count = len(user_message)
        token_count = character_count / 4

        # Show token estimate
        st.info(
            f"System Check: Your message will consume approximately {token_count:.2f} tokens from our context window."
        )
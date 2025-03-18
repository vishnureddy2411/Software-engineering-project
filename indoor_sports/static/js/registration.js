document.addEventListener("DOMContentLoaded", function () {
    // Retrieve the CSRF token from the page
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Get references to relevant DOM elements
    const emailInput = document.getElementById("emailid");
    const emailError = document.getElementById("email-error"); // Make sure this element exists in your template, if needed
    const usernameInput = document.getElementById("username");
    const usernameError = document.getElementById("username-error"); // Make sure this element exists in your template, if needed

    const registrationForm = document.getElementById("registration-form");
    const zipcodeInput = document.getElementById("zip_code");
    const cityInput = document.getElementById("city");
    const stateInput = document.getElementById("state");
    const countryInput = document.getElementById("country");

    // AJAX Email Validation if emailInput is not readonly
    if (emailInput && !emailInput.readOnly) {
        emailInput.addEventListener("input", async function () {
            const email = this.value.trim();
            if (email.length > 0) {
                try {
                    const response = await fetch(checkEmailUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded"
                        },
                        body: new URLSearchParams({
                            "emailid": email,
                            "csrfmiddlewaretoken": csrfToken
                        })
                    });
                    const data = await response.json();
                    // Provide visual feedback based on response
                    if (data.exists) {
                        if (emailError) emailError.style.display = "block";
                        emailInput.style.borderColor = "red";
                    } else {
                        if (emailError) emailError.style.display = "none";
                        emailInput.style.borderColor = "green";
                    }
                } catch (error) {
                    console.error("Error checking email:", error);
                }
            } else {
                if (emailError) emailError.style.display = "none";
                emailInput.style.borderColor = "";
            }
        });
    }

    // AJAX Username Validation if usernameInput is not readonly
    if (usernameInput && !usernameInput.readOnly) {
        usernameInput.addEventListener("input", async function () {
            const username = this.value.trim();
            if (username.length > 0) {
                try {
                    const response = await fetch(checkUsernameUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "X-CSRFToken": csrfToken
                        },
                        body: new URLSearchParams({
                            "username": username
                        })
                    });
                    const data = await response.json();
                    if (data.exists) {
                        if (usernameError) usernameError.style.display = "block";
                        usernameInput.style.borderColor = "red";
                    } else {
                        if (usernameError) usernameError.style.display = "none";
                        usernameInput.style.borderColor = "green";
                    }
                } catch (error) {
                    console.error("Error checking username:", error);
                }
            } else {
                if (usernameError) usernameError.style.display = "none";
                usernameInput.style.borderColor = "";
            }
        });
    }

    // Basic form validation function for user registration
    function validateUserForm() {
        const email = emailInput ? emailInput.value.trim() : "";
        const phone = document.getElementById("contactnumber") ? document.getElementById("contactnumber").value.trim() : "";
        const password = document.getElementById("password") ? document.getElementById("password").value.trim() : "";

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phonePattern = /^[0-9]{10}$/;

        if (!emailPattern.test(email)) {
            alert("Enter a valid email address.");
            return false;
        }
        if (phone && !phonePattern.test(phone)) {
            alert("Enter a valid 10-digit phone number.");
            return false;
        }
        if (password.length < 6) {
            alert("Password must be at least 6 characters long.");
            return false;
        }
        return true;
    }

    // Form submission handler with final validation check
    if (registrationForm) {
        registrationForm.addEventListener("submit", function (e) {
            if (!validateUserForm()) {
                e.preventDefault();
            }
        });
    }

    // Zip Code to Location Mapping using Positionstack API
    if (zipcodeInput) {
        zipcodeInput.addEventListener("input", async function () {
            const zipcode = this.value.trim();
            // Proceed if zipcode length is at least 3 and matches allowed format
            if (zipcode.length >= 5 && /^[a-zA-Z0-9\s]*$/.test(zipcode)) {
                try {
                    // For production, consider routing this request through your Django backend to mask the API key.
                    const response = await fetch(`http://api.positionstack.com/v1/forward?access_key=a2535033f9f71d56bf960a1f43fab42f&query=${zipcode}, United States`);
                    const data = await response.json();
                    if (data.data && data.data.length > 0) {
                        const place = data.data[0]; // use the first result
                        if (stateInput) stateInput.value = place.region || '';
                        if (cityInput) cityInput.value = place.locality || '';
                        if (countryInput) countryInput.value = place.country || 'United States';
                    } else {
                        if (cityInput) { cityInput.value = ''; cityInput.disabled = false; }
                        if (stateInput) { stateInput.value = ''; stateInput.disabled = false; }
                        if (countryInput) { countryInput.value = 'United States'; countryInput.disabled = false; }
                        alert("No data found for this zip code. Please enter city, state, and country manually.");
                    }
                } catch (error) {
                    console.error("Error fetching location details:", error);
                    alert("There was an error fetching the data. Please enter city, state, and country manually.");
                }
            } else {
                // Reset location fields if zip code input is cleared or invalid
                if (cityInput) { cityInput.value = ''; cityInput.disabled = false; }
                if (stateInput) { stateInput.value = ''; stateInput.disabled = false; }
                if (countryInput) { countryInput.value = 'United States'; countryInput.disabled = false; }
                console.log("Invalid zip code format. Please enter a valid zip code.");
            }
        });
    }
});

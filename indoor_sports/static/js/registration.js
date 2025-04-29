document.addEventListener("DOMContentLoaded", function () {
    // Retrieve CSRF token (optional use for AJAX calls requiring CSRF protection)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Get references to input fields
    const zipcodeInput = document.getElementById("zip_code");
    const cityInput = document.getElementById("city");
    const stateInput = document.getElementById("state");
    const countryInput = document.getElementById("country");
    const emailInput = document.getElementById("emailid");
    const emailError = document.getElementById("email-error");
    const usernameInput = document.getElementById("username");
    const usernameError = document.getElementById("username-error");
    const registrationForm = document.getElementById("registration-form");

    // ------------------- ZIP Code Location Fetching -------------------
    if (zipcodeInput) {
        console.log("ZIP Code input field detected."); // Debugging confirmation

        // Attach an event listener to the ZIP Code input
        zipcodeInput.addEventListener("input", async function () {
            const zipcode = this.value.trim();
            console.log("Entered ZIP Code:", zipcode); // Debugging
            if (zipcode.length >= 5 && /^[0-9]{5,10}$/.test(zipcode)) {
                const baseUrl = window.location.origin; // Dynamically detects deployment URL
                const fetchUrl = `${baseUrl}/register/user/get-location/?zipcode=${zipcode}`;

                console.log("Fetch Request URL:", fetchUrl); // Debugging



                try {
                    // Adjust fetch URL to match the backend endpoint
                    const response = await fetch(`/register/user/get-location/?zipcode=${zipcode}`);
                    console.log("Fetch Request URL:", `/register/user/get-location/?zipcode=${zipcode}`); // Debugging

                    if (!response.ok) {
                        throw new Error(`API call failed with status ${response.status}`);
                    }

                    const data = await response.json();
                    console.log("API Response Data:", data); // Debugging

                    // Populate the city, state, and country fields
                    if (data.region) stateInput.value = data.region || '';
                    if (data.locality) cityInput.value = data.locality || '';
                    if (data.country) countryInput.value = data.country || 'United States';
                } catch (error) {
                    console.error("Error fetching location data:", error); // Debugging
                    alert("There was an error fetching the location details. Please enter city, state, and country manually.");
                }
            } else {
                console.log("Invalid ZIP Code format."); // Debugging
                stateInput.value = '';
                cityInput.value = '';
                countryInput.value = 'United States';
            }
        });
    } else {
        console.error("ZIP Code input field not found."); // Debugging
    }

    // ------------------- Email Validation Logic -------------------
    if (emailInput && !emailInput.readOnly) {
        emailInput.addEventListener("input", async function () {
            const email = this.value.trim();
            if (email.length > 0) {
                try {
                    const response = await fetch(checkEmailUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        body: new URLSearchParams({
                            emailid: email,
                            csrfmiddlewaretoken: csrfToken
                        })
                    });

                    const data = await response.json();
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

    // ------------------- Username Validation Logic -------------------
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
                            username: username
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

    // ------------------- Form Validation -------------------
    if (registrationForm) {
        registrationForm.addEventListener("submit", function (e) {
            // Perform validation before form submission
            if (!validateForm()) {
                e.preventDefault();
                alert("Please fix the errors in the form before submitting.");
            }
        });
    }

    function validateForm() {
        const zipcode = zipcodeInput?.value.trim();
        const city = cityInput?.value.trim();
        const state = stateInput?.value.trim();
        const country = countryInput?.value.trim();

        if (!zipcode || zipcode.length < 5) {
            alert("Please enter a valid ZIP Code.");
            return false;
        }
        if (!city) {
            alert("City cannot be empty.");
            return false;
        }
        if (!state) {
            alert("State cannot be empty.");
            return false;
        }
        if (!country) {
            alert("Country cannot be empty.");
            return false;
        }
        return true;
    }
});
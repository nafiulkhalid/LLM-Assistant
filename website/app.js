document.addEventListener("DOMContentLoaded", () => {
    gsap.registerPlugin(ScrollTrigger);

    // Ensure Bootstrap navbar toggle works
    document.querySelector(".navbar-toggler").addEventListener("click", () => {
        document.querySelector("#navbarNav").classList.toggle("show");
    });

    // Navbar Scroll Effect
    const navbar = document.querySelector(".navbar");
    const navLinks = document.querySelectorAll(".nav-link");
    const navbarBrand = document.querySelector(".navbar-brand");

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.classList.add("navbar-scrolled");
            navbarBrand.style.color = "white";
            navLinks.forEach(link => link.style.color = "white");
            document.querySelector(".navbar-toggler-icon").style.filter = "invert(1)"; // Make icon white
        } else {
            navbar.classList.remove("navbar-scrolled");
            navbarBrand.style.color = "black";
            navLinks.forEach(link => link.style.color = "black");
            document.querySelector(".navbar-toggler-icon").style.filter = "invert(0)"; // Make icon black
        }
    });

    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            document.querySelector("#navbarNav").classList.remove("show"); // Close menu on click
        });
    });

    // Hero Section Animation
    let tl = gsap.timeline({
        scrollTrigger: {
            trigger: "#hero",
            start: "top top",
            end: "+=100%",
            scrub: 1.2,
            pin: "#hero",
            anticipatePin: 1,
        }
    });

    tl.to(".letter-a", { x: "-100vw", duration: 1.8, ease: "power2.out" }, 0);
    tl.to(".letter-e", { x: "-50vw", duration: 1.8, ease: "power2.out" }, 0);
    tl.to(".letter-r", { x: "50vw", duration: 1.8, ease: "power2.out" }, 0);
    tl.to(".letter-o", { x: "100vw", duration: 1.8, ease: "power2.out" }, 0);

    // Fade out tagline first
    tl.to(".tagline", { opacity: 0, duration: 0.8, ease: "power1.out" }, "-=1");

    // Fade-in animations for sections
    gsap.from(".how-card", {
        opacity: 0,
        y: 50,
        duration: 1,
        stagger: 0.3,
        scrollTrigger: {
            trigger: "#how-it-works",
            start: "top 80%",
            toggleActions: "play none none reverse"
        }
    });

    gsap.from("#aero-benefits-image", {
        opacity: 0,
        x: -50,
        duration: 1,
        scrollTrigger: {
            trigger: "#why-choose-aero",
            start: "top 80%",
            toggleActions: "play none none reverse"
        }
    });

    gsap.from(".aero-benefits-list li", {
        opacity: 0,
        x: 50,
        duration: 1,
        stagger: 0.3,
        scrollTrigger: {
            trigger: "#why-choose-aero",
            start: "top 80%",
            toggleActions: "play none none reverse"
        }
    });

    // Contact Form Submission Handling
    document.getElementById("contact-form").addEventListener("submit", function(event) {
        event.preventDefault();

        let name = document.getElementById("name").value;
        let email = document.getElementById("email").value;
        let message = document.getElementById("message").value;

        if (name && email && message) {
            alert(`Thank you, ${name}! Your message has been sent.`);
            document.getElementById("contact-form").reset();
        } else {
            alert("Please fill in all fields.");
        }
    });

    // Improved Beta Form UX
    const betaForm = document.querySelector(".beta-form");
    const betaEmail = document.getElementById("beta-email");
    const betaMessage = document.getElementById("beta-message");
    const betaButton = document.querySelector(".beta-button");

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Real-time email validation
    betaEmail.addEventListener("input", () => {
        if (!isValidEmail(betaEmail.value)) {
            betaMessage.innerText = "❌ Please enter a valid email (must contain '@' and end with '.com')";
            betaMessage.style.color = "red";
        } else {
            betaMessage.innerText = "";
        }
    });

    betaButton.addEventListener("click", function (event) {
        event.preventDefault();

        if (!isValidEmail(betaEmail.value)) {
            betaMessage.innerText = "❌ Please enter a valid email (must contain '@' and end with '.com')";
            betaMessage.style.color = "red";
            return;
        }

        // Show loading indicator on the button
        betaButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting...`;
        betaButton.disabled = true;

        // Simulate a network request
        setTimeout(() => {
            betaMessage.innerText = `✅ Successfully joined the beta!`;
            betaMessage.style.color = "green";

            // Reset form after success
            betaEmail.value = "";

            // Reset button after submission
            betaButton.innerHTML = "Joined Beta Waitlist";
            betaButton.disabled = false;
        }, 1500);
    });
});

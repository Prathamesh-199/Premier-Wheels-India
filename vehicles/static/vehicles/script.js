document.addEventListener("DOMContentLoaded", function () {

    /*
     * ==========================================
     * Indian number formatting
     * ==========================================
     */

    function formatIndianNumber(value) {

        let number = value.replace(/[^\d]/g, "");

        if (!number) {
            return "";
        }

        if (number.length <= 3) {
            return number;
        }

        const lastThree = number.slice(-3);
        let otherNumbers = number.slice(0, -3);

        otherNumbers = otherNumbers.replace(
            /\B(?=(\d{2})+(?!\d))/g,
            ","
        );

        return otherNumbers + "," + lastThree;
    }


    function formatIndianPrice(value) {

        const number = formatIndianNumber(value);

        if (!number) {
            return "";
        }

        return "₹" + number;
    }


    const priceInputs =
        document.querySelectorAll(".price-input");


    priceInputs.forEach(function (input) {

        if (input.value) {
            input.value =
                formatIndianPrice(input.value);
        }


        input.addEventListener(
            "input",
            function () {

                input.value =
                    formatIndianPrice(input.value);

            }
        );

    });


    const mileageInputs =
        document.querySelectorAll(".mileage-input");


    mileageInputs.forEach(function (input) {

        if (input.value) {
            input.value =
                formatIndianNumber(input.value);
        }


        input.addEventListener(
            "input",
            function () {

                input.value =
                    formatIndianNumber(input.value);

            }
        );

    });


    /*
     * ==========================================
     * Search price formatting
     * ==========================================
     */

    const filterPriceInputs =
        document.querySelectorAll(".filter-price-input");

    filterPriceInputs.forEach(function (input) {

        if (input.value) {
            input.value = formatIndianNumber(input.value);
        }

        input.addEventListener("input", function () {
            input.value = formatIndianNumber(input.value);
        });
    });


    /*
     * ==========================================
     * Delete confirmation
     * ==========================================
     */

    const deleteForms =
        document.querySelectorAll(".delete-form");


    deleteForms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const confirmed = confirm(
                    "Are you sure you want to delete this vehicle?"
                );


                if (!confirmed) {
                    event.preventDefault();
                }

            }
        );

    });


    /*
     * ==========================================
     * Hide success messages
     * ==========================================
     */

    window.setTimeout(function () {

        const messages =
            document.querySelectorAll(".message");


        messages.forEach(function (message) {

            message.style.transition =
                "opacity 0.5s ease, transform 0.5s ease";

            message.style.opacity = "0";
            message.style.transform = "translateY(-8px)";

        });

    }, 4500);

});


    /*
     * ==========================================
     * Vehicle photo gallery
     * ==========================================
     */

    const mainVehicleImage =
        document.getElementById("mainVehicleImage");

    const photoThumbnails =
        document.querySelectorAll(".photo-thumbnail");

    photoThumbnails.forEach(function (thumbnail) {

        thumbnail.addEventListener("click", function () {

            const imageUrl =
                thumbnail.getAttribute("data-image");

            if (!mainVehicleImage || !imageUrl) {
                return;
            }

            if (mainVehicleImage.tagName === "IMG") {
                mainVehicleImage.src = imageUrl;
            } else {
                const replacement =
                    document.createElement("img");

                replacement.src = imageUrl;
                replacement.alt = "Vehicle photo";
                replacement.className =
                    "detail-image gallery-main-image";
                replacement.id = "mainVehicleImage";

                mainVehicleImage.replaceWith(replacement);
            }

            photoThumbnails.forEach(function (item) {
                item.classList.remove("active");
            });

            thumbnail.classList.add("active");

        });

    });


/*
 * ==========================================
 * Premier Wheels Ownership Estimate
 * ==========================================
 */

document.addEventListener("DOMContentLoaded", function () {

    const ownershipCalculator =
        document.getElementById("ownership-calculator");

    if (!ownershipCalculator) {
        return;
    }

    const annualKmInput =
        document.getElementById("ownershipAnnualKm");

    const fuelPriceInput =
        document.getElementById("ownershipFuelPrice");

    const efficiencyInput =
        document.getElementById("ownershipEfficiency");

    const insuranceInput =
        document.getElementById("ownershipInsurance");

    const maintenanceInput =
        document.getElementById("ownershipMaintenance");

    const calculateButton =
        document.getElementById("calculateOwnership");

    const result =
        document.getElementById("ownershipResult");

    const fuelCostOutput =
        document.getElementById("ownershipFuelCost");

    const annualTotalOutput =
        document.getElementById("ownershipAnnualTotal");

    const fiveYearOutput =
        document.getElementById("ownershipFiveYearTotal");

    const efficiencyHint =
        document.getElementById("ownershipEfficiencyHint");

    const fuelType =
        ownershipCalculator.getAttribute("data-fuel-type") || "petrol";

    const defaults = {
        petrol: { efficiency: 15, rate: 100, unit: "₹/litre" },
        diesel: { efficiency: 18, rate: 90, unit: "₹/litre" },
        cng: { efficiency: 20, rate: 90, unit: "₹/kg" },
        hybrid: { efficiency: 18, rate: 100, unit: "₹/litre" },
        electric: { efficiency: 6, rate: 10, unit: "₹/kWh" }
    };

    const selected =
        defaults[fuelType] || defaults.petrol;

    efficiencyInput.value = selected.efficiency;
    fuelPriceInput.value = "";
    fuelPriceInput.placeholder =
        "Example " + selected.rate + " " + selected.unit;

    efficiencyHint.textContent =
        "Example assumption for " +
        fuelType +
        ": " +
        selected.efficiency +
        " km/unit. Edit it for this car.";

    calculateButton.addEventListener("click", function () {

        const annualKm = Number(annualKmInput.value);
        const fuelPrice = Number(fuelPriceInput.value);
        const efficiency = Number(efficiencyInput.value);
        const insurance = Number(insuranceInput.value) || 0;
        const maintenance = Number(maintenanceInput.value) || 0;

        if (
            annualKm <= 0 ||
            fuelPrice <= 0 ||
            efficiency <= 0
        ) {
            alert(
                "Please enter valid annual driving, fuel/energy price and efficiency."
            );
            return;
        }

        const energyRequired = annualKm / efficiency;
        const annualFuelCost = energyRequired * fuelPrice;
        const annualTotal =
            annualFuelCost + insurance + maintenance;
        const fiveYearTotal = annualTotal * 5;

        const formatCurrency = function (value) {
            return "₹" +
                Math.round(value).toLocaleString("en-IN");
        };

        fuelCostOutput.textContent =
            formatCurrency(annualFuelCost);

        annualTotalOutput.textContent =
            formatCurrency(annualTotal);

        fiveYearOutput.textContent =
            formatCurrency(fiveYearTotal);

        result.hidden = false;
    });
});

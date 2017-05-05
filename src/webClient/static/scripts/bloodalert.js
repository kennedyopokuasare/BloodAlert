
bloodTypes = []

DEFUALT_DATA_TYPE = "json"

function loadBloodTypes(event) {
    return $.ajax({
        url: "/bloodalert/bloodtypes",
        dataType: DEFUALT_DATA_TYPE
    }).done(function (data, textStatus, jqXHR) {
        bloodTypes = data.items;
        if (data.items.length > 0) {
            $dropdown = $("#bloodTypeId");
            $dropdown.append(
                $('<option></option>').val("").html("Select Blood Type")
            );
            $.each(data.items, function (index, item) {
                $dropdown.append(
                    $('<option></option>').val(item.bloodTypeId).html(item.name)
                );
            });
        }
       
    });
}
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
           
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function handleLoginDonorButton(event) {
    var $form = $(this).closest("form");
   
    $data = serializeFormTemplate($form)
   
    return $.ajax({
        url: "/bloodalert/donors/",
        dataType: DEFUALT_DATA_TYPE
    }).done(function (data, textStatus, jqXHR) {

        for (var i = 0; i < data.items.length; i++) {
            item = data.items[i];
            if (item.email.toLowerCase() == $data.email.toLowerCase()) {
                setCookie("BloodAlertLoggedInDonor", JSON.stringify(item), 1)
                window.open("http://" + window.location.host + "/web/profile", "_self")
                window.loggedInUser = item;
            }
        }

       
    });
}

function handleDonorRegistration(event) {
    var $form = $(this).closest("form");
    
    $data = serializeFormTemplate($form)
}

function serializeFormTemplate($form) {
    var envelope = {};
    // get all the inputs into an array.
    var $inputs = $form.find(".form-group .form-control");
    $inputs.each(function () {
        envelope[this.id] = $(this).val();
    });

    var subforms = $form.find(".form_content .subform");
    subforms.each(function () {

        var data = {}

        $(this).children("input").each(function () {
            data[this.id] = $(this).val();
        });

        envelope[this.id] = data
    });
    return envelope;
}
function getNoAuthPages() {
    noAuthPages = []
    noAuthPages.push("http://" + window.location.host + "/web/contact")
    noAuthPages.push("http://" + window.location.host + "/web/register")
    noAuthPages.push("http://" + window.location.host + "/web/about")
    return noAuthPages;
}
function checkLoggedinDonor() {
    currentpage = window.location.href;


    var cookie = getCookie("BloodAlertLoggedInDonor");
    
    if (cookie != "") {
        hideLoginForm();
        redressMenuAfterLogin();
        window.loggedInUser = $.parseJSON(cookie);
    } else {

        loginPage = "http://" + window.location.host + "/web/" || "http://" + window.location.host + "/web";
        
        if (currentpage != loginPage) {
            noAuthPages = getNoAuthPages()
            if (noAuthPages.indexOf(currentpage) == -1)
                window.open(loginPage, "_self")
        }

    }
}

function logOutDonor() {

    Cookies.remove('BloodAlertLoggedInDonor', { path: '/' })
    window.loggedInUser = undefined
    delete window.loggedInUser
    
    loginPage = "http://" + window.location.host + "/web/" || "http://" + window.location.host + "/web";
    window.open(loginPage, "_self")
}

function hideLoginForm() {
    $("#DonorLoginFormDiv").remove();
    $("#indexBloodLevels").removeClass("col-md-8").addClass("col-md-12");
}
function redressMenuAfterLogin() {
    profileUrl="http://" + window.location.host + "/web/profile";
    $(".navbar-nav").append('<li><a  href="'+profileUrl+'">Profile</a></li>');
    $(".navbar-nav").append('<li><a id="LogOutLink" href="#">Log Out</a></li>');
    $(".navbar-nav > #DonorRegistrationMenu").remove();
}


$(function () {
   checkLoggedinDonor();
    $("#loginDonorButton").click(handleLoginDonorButton);
    $("#donorRegisterbtn").click(handleDonorRegistration);
    $("#LogOutLink").click(logOutDonor);
    loadBloodTypes();
});

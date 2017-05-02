
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
        console.log(data)
    });
}
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
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

function checkCookie() {
    var user = getCookie("username");
    if (user != "") {
        alert("Welcome again " + user);
    } else {
        user = prompt("Please enter your name:", "");
        if (user != "" && user != null) {
            setCookie("username", user, 365);
        }
    }
}
function handleLoginDonorButton(event) {
    var $form = $(this).closest("form");
    console.log("submit")
    $data = serializeFormTemplate($form)
    console.log($data)
    return $.ajax({
        url: "/bloodalert/donors/",
        dataType: DEFUALT_DATA_TYPE
    }).done(function (data, textStatus, jqXHR) {
        
        for(var i=0;i<data.items.length;i++){
            item=data.items[i];
            if(item.email==$data.email){
                document.cookie()
                console.log(item);
                window.loggedInUser=item;

                window.open("http://"+window.location.host+ "/web/profile",)
                window.loggedInUser=item;
            }
        }

        console.log(data)
    });
}

function handleDonorRegistration(event) {
    var $form = $(this).closest("form");
    console.log("submit")
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

$(function () {

    $("#loginDonorButton").click(handleLoginDonorButton);
    $("#donorRegisterbtn").click(handleDonorRegistration);

    loadBloodTypes();

});

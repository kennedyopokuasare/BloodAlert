var gender;
var bloodTypeID;

$(function () {
    //highlight My profile menu
    $("#myProfileMenu").css({'background':'darkred', 'color':'white'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'white', 'color':'black'});

    /**
     * here client code depicts a true hypermedia behavior, 
     * by using hypermdia links to find URLs
     */
    donorUrl=window.loggedInUser["@controls"].self.href
    bloodTypeUrl=window.loggedInUser["@controls"].bloodtype.href
    $.ajax({
        url: donorUrl,
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
    
       
        $("#firstName_edit").val(data.firstname);
        $("#lasttName_edit").val(data.familyName);
        $("#birthday_edit").val(data.birthDate.slice(8,10) + "-" + data.birthDate.slice(5,7) + "-" +data.birthDate.slice(0,4));
        gender = data.gender;
        if (gender.toLowerCase()=="female"){$("#id_gender_female").attr('checked', true);}
        else {$("#id_gender_male").attr('checked', true);}
        bloodTypeID = data.bloodTypeId;
        switch(bloodTypeID){
            case "btype-1":
                $("#bloodType_edit").text("O+");
                break;
            case "btype-2":
                $("#bloodType_edit").text("O-");
                break;
            case "btype-3":
                $("#bloodType_edit").text("A+");
                    break;
            case "btype-4":
                $("#bloodType_edit").text("A-");
                    break;
            case "btype-5":
                $("#bloodType_edit").text("B+");
                    break;
            case "btype-6":
                $("#bloodType_edit").text("B-");
                    break;
            case "btype-7":
                $("#bloodType_edit").text("AB+");
                    break;
            case "btype-8":
                $("#bloodType_edit").text("AB-");
        }
        $("#phoneNumber").val(data.telephone)
        $("#city_edit").val(data.city)
        $("#address_edit").val(data.address)
        $("#id_email").val(data.email)   
    });
});

$("#profileEdite_save").click(function(){
    /**
     * here client code depicts a true hypermedia behavior, 
     * by using hypermdia links to find URLs
     */
    donorUrl=window.loggedInUser["@controls"].self.href
    bloodTypeUrl=window.loggedInUser["@controls"].bloodtype.href

    var bodyJSON = new Object();
    bodyJSON = {
        "firstname" : $("#firstName_edit").val(),
        "familyName" : $("#lasttName_edit").val(),
        "birthDate": $("#birthday_edit").val(),
        "gender" : gender,
        "bloodTypeId" : bloodTypeID,
        "telephone": $("#phoneNumber").val(),
        "city": $("#city_edit").val(),
        "address": $("#address_edit").val(),
        "email": $("#id_email").val()
    }

    $.ajax({
        url: donorUrl,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        type: 'PUT',
        headers: { "Content-Type": "application/json"},
        data: JSON.stringify(bodyJSON),
    }).done(function (data, textStatus, jqXHR) {
        window.open("http://" + window.location.host + "/web/profile", "_self")
    });
});

$('#bloodTypeList li').click(function() {
    $("#bloodType_edit").text(this.id);
    switch(this.id){
            case "O+":
                bloodTypeID = "btype-1";
                break;
            case "O-":
                bloodTypeID = "btype-2";
                break;
            case "A+":
                bloodTypeID = "btype-3";
                    break;
            case "A-":
                bloodTypeID = "btype-4";
                    break;
            case "B+":
                bloodTypeID = "btype-5";
                    break;
            case "B-":
                bloodTypeID = "btype-6";
                    break;
            case "AB+":
                bloodTypeID = "btype-7";
                    break;
            case "AB-":
                bloodTypeID = "btype-8";
        }
})

$("#id_gender_female").click(function(){
    gender = "Female";
})

$("#id_gender_male").click(function(){
    gender = "Male";
})



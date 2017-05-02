
$(function () {
    $.ajax({
        url: "/bloodalert/donors/bdonor-2",
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
    
        //console.log(data)
        $("#fullNanme").text(data.firstname + " " + data.familyName)
        $("#birthday").text(" " + data.birthDate)
        $("#gender").text(" " + data.gender)
        $("#bloodTypeID").text(" " + data.bloodTypeId)
        $("#phone").text(" " + data.telephone)
        $("#cityAddress").text(" " + data.city + ", " + data.address)
        $("#email").text(" " + data.email)
        
        
    });
});

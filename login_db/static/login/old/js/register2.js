$(document).ready(function()
{
// Popover 
$('#registerHere input').hover(function()
{
$(this).popover()
});
//password validation
$('form').on('submit',function(){

var invalid = " "; // Invalid character is a space
var minLength = 6; // Minimum length
var phoneNo= /^\d{10}$/;
   if($('#pwd').val()!=$('#cpwd').val()){
       alert('Passwords do not match.');
       return false;
   }
   
   else
   {
	   if($('#pwd').val().length< minLength){
		   alert('Password must be aleast 6 characters long. Try again.');
		   return false;
	   }
	   
	   else‮
	   {
		   if($('#pwd').val().indexOf(invalid)>-1){
			   alert('Sorry, spaces are not allowed.');
			   return false;
		   }
		   else
		   {
		   		if( !($('#phone').val().match(phoneNo)) ){
			   		alert('Only 10 DIGITS allowed in phone number.');
			   		return false;
		       }


		   }
	   }
   }
   return true;
});


// Validation-Register
$("#registerHere").validate({
rules:{
name:"required",
user_email:{required:true,email: true},
pwd:{required:true,minlength: 6},
cpwd:{required:true,equalTo: "#pwd"},
gender:"required"
},

messages:{
user_name:"Enter your first and last name",
user_email:{
required:"Enter your email address",
email:"Enter valid email address"},
pwd:{
required:"Enter your password",
minlength:"Password must be minimum 6 characters"},
cpwd:{
required:"Enter confirm password",
equalTo:"Password and Confirm Password must match"},
},


errorClass: "help-inline",
errorElement: "span",
highlight:function(element, errorClass, validClass)
{
$(element).parents('.control-group').addClass('error');
},
unhighlight: function(element, errorClass, validClass)
{
$(element).parents('.control-group').removeClass('error');
$(element).parents('.control-group').addClass('success');
}
});
});

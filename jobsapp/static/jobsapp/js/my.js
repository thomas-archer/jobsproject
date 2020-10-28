 // Expand/Collapse button for jobposts view
 $( document ).ready(function() {

  $( "#collapsebutton" ).hide();

  $( "#expandbutton" ).click(function() {
  $('div.collapse').addClass('show').css("height", "");
  $( "#expandbutton" ).hide();
  $( "#collapsebutton" ).show();
  });

  $( "#collapsebutton" ).click(function() {
  $('div.collapse').removeClass('show');
  $( "#expandbutton" ).show();
  $( "#collapsebutton" ).hide();
  });

  $( "div.collapse" ).click(function() {
    $('div.collapse').each(function( index ) {
      if($( this ).hasClass('in') ){
      $( "#expandbutton" ).show();
      $( "#collapsebutton" ).hide();
      }
    });
  });

}); 

// Apply for a single jobpost
$('.apply-button').on('click',function() {
  $("body").addClass("loading");
  var tempid;
  tempid = $(this).attr("data-jobid");
  $.ajax({
    type:"GET",
    url: "/applytojob",
    data:{
          jobpost_id: tempid
    },
    success: function( data ) 
    {
        $("body").removeClass("loading");
        $( '#message' ).text(data);
        if(data!="Success") {
          if(data=="Post no longer exists") {
            alert("This post has expired. Removing from list.")
            cardid = '#card'+tempid
            $(cardid).remove();
          }
          else if(data=="missing_profile_info") {
            alert("It looks like your profile is missing information. Please fill it in or apply manually.")
          }
          else if(data=="post_aleady_applied_to") {
            alert("You have already applied to this post.")
            $( '#apply'+ tempid ).replaceWith('<p class="btn main-button applied-button">Applied</p>')
          }
          else {
            if(confirm("Oops! We hit a snag while autofilling your application. Would you like to complete it manually?")) {
              window.open(
                data,
                '_blank' // <- This is what makes it open in a new window.
              );
            }
          }
        }
        else {
          $( '#apply'+ tempid ).replaceWith('<p class="btn main-button applied-button">Applied</p>')
        }
    }
  })
});



//Apply for all available jobposts
$('.applyallbutton').on('click',function() {
  if (confirm('Are you sure you want to apply to all jobs? This may take a couple minutes.')) {
    $("body").addClass("loading");
    $.ajax({
      type:"GET",
      url: "/applyalljobs",
      data:{

      },
      success: function ( data )
      {
        //Gotta replace jobposts with applied or remove them or reresh page
        if(data=="missing_profile_info") {
          alert("It looks like your profile is missing information. Please fill it in or apply manually.")
        }
        else {
          $( '.applyallbutton').replaceWith('<p class="btn main-button" style="float: right;">Applied to all!</p>')
          $('.applybutton').replaceWith('<p class="btn btn-success appliedbutton" style="float: right;">Applied</p>')
          $( '#message' ).text(data);
          if(data!="Success") {
            alert(`Looks like we missed a couple! Autofill was unable to apply to ${data} job posts. They will remain in your list the next time you visit this page.`)
          }
        }
        $("body").removeClass("loading");
      }
    })
  }
});


// Remove a jobpost
$('.removebutton').on('click',function() {
  var tempid;
  tempid = $(this).attr("data-jobid");
  $.ajax({
    type:"GET",
    url: "/removejob",
    data:{
          jobpost_id: tempid
    },
    success: function( data ) 
    {
      cardid = '#card'+tempid
      $(cardid).hide('slow', function(){ $target.remove();});
    }
  })
});


// Remove a jobquery
function removeQuery(clicked_id) {
  // alert(clicked_id);
  $.ajax({
    type:"GET",
    url: "/removejobquery",
    data:{
          jobquery_id: clicked_id
    },
    success: function( data ) 
    {
      // chipid = '#chip'+clicked_id
      // $(chipid).remove()
      location.reload(true);
    }
  })       
}

function testFunc() {
  // alert(clicked_id);
  $.ajax({
    type:"GET",
    url: "/testfunc",
    data:{
          
    },
    success: function( data ) 
    {
      alert('clicked!')
      // location.reload(true);
    }
  })       
}








//Scroll button on home page
// function scrollFunc() {
//   $('html, body').animate({scrollTop: 850 }, 1100);
//     return false;
// }








// Old preloader JS
// $(window).on('load', function () {
//   if ($('.cover').length) {
//       $('.cover').parallax({
//           imageSrc: $('.cover').data('image'),
//           zIndex: '1'
//       });
//   }

//   $("#preloader").animate({
//       'opacity': '0'
//   }, 600, function () {
//       setTimeout(function () {
//           $("#preloader").css("visibility", "hidden").fadeOut();
//       }, 300);
//   });
// });

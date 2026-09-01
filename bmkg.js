const api = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=32.17.01.2004";

fetch(api)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(userData => {

    // Debug Data BMKG
    const cuaca1 = userData.data[0].cuaca;
    
    cuaca1.forEach(element => {
      element.forEach(item => {
          console.log("data " ,item);
      });
    });
  })
  .catch(error => {
    console.error('Error:', error);
  });

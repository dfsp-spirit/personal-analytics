# personal-analytics ChangeLog

## Version 0.2.0 -- Final measures list, many fixes
* Update measures: remove social_support, anxiety. Add step_count, sexual_wellbeing.
* Way better documentation, especially on deployment
* Remove everything related to Docker
* Add settings.py file for backend and move all settings there
* Considerably extend the frontend statistics page
* Export and import functionality via JSON, export via CSV
* Fix error reporting in backend: add CORS headers in case of error, so that internal server error does not masquerade as CORS issue for frontend
* Way more secure default settings for service and created database


## Version 0.1.0 -- First release
* The first version deployed to the test server on the internet
* features include:
    - frontend that can be filled out easily on desktop and mobile
    - htaccess-based protection for backend and frontend
    - inputs for radio button, slider, text area, (multi-) check box
    - data stored in postgredql database
    - support for displaying basic stats in frontend on extra page
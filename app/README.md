
# NPM INSTALLATION
Install npm locally in `app` directory with
```cd app```
``` npm install npm --save-dev```

## DEPENDECIES
```npm install react-datepicker dayjs @mui/x-date-pickers @mui/material @emotion/react @emotion/styled```

## DEPLOY
```npm run dev```

## FRONTEND STRUCTURE
### directories:
`\public` - contains displayed data such as `heatmap.svg` or list of stops  <br />
`\app` - contains `.tsx` files responsible for creating sites  <br />
`\components` - contains `.js` files and `.css` files responsible for dynamin element and layout  <br />

### \app files
`page.tsx` - main page  <br />
`search\page.tsx` - page that displays dropdown menu with all avaiable stops, map with heatmap overlay, time picker and search button  <br />

### \components files
`Button.js` - dynamic button mechanics <br />
`Datetime.js` - dynamic picker component for chosing date and time which also passes chosen time for search and algorithm purposes <br />
`Map.js` - dynamic map component, enables putting a pin on map which results in defining nearest stop, displaying current heatmap for chosen start stop, displays chosen start stop <br />
`SearchDropDown.js` - dynamic drop down menu with list of all stops presented, handles choosing start stop, passing its name for map display, also handles sending data for creating heatmap <br />


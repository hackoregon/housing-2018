packages = {  
  'Evictions': {
    'description': '',
    #'Eviction, rent, income, and property values by census blockgroup.',
    'foundations' : ['018', '019', '020', '021', '022', '043'],
    'default_foundation' : '020',
    'slides' : ['014',  '009', '011', '017'],
    'default_slide' : ['011']
    },
  }


"""
 Slides: 
 Used in formulating the package definitions
"""
slides = {
  '009': {
    'name': 'rail stops',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/slides/railstops/',
    'visualization': 'ScatterPlotMap',
  },  
  '011': {
    'name': 'demolitions',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/slides/demolitions/',
    'visualization': 'ScatterPlotMap',
  }, 
  '014': {
    'name': 'bus stops',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/slides/busstops/',
    'visualization': 'ScatterPlotMap',
  },
  '017': {
    'name': 'Building Permits',
    'endpoint':'http://service.civicpdx.org/housing-affordability/sandbox/slides/permits/',
    'visualization': 'ScreenGridMap',
  },
}

"""
 Foundations:
 Used in formulating the package definitions
"""
foundations = {
  '018': {
    'name': 'Median Household Income',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/income/',
    'visualization': 'ChoroplethMap',
  },
  '019': {
    'name': 'Median Gross Rent',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/grossrent/',
    'visualization': 'ChoroplethMap',
  },
  '020': {
    'name': 'Evictions',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/evictions/',
    'visualization': 'ChoroplethMap',
  },
  '021': {
    'name': 'Renter Occupied Households',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/renteroccupied/',
    'visualization': 'ChoroplethMap',
  },
  '022': {
    'name': 'Rent Burden',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/rentburden/',
    'visualization': 'ChoroplethMap',
  },
  '043': {
    'name': 'Eviction Rate',
    'endpoint':'http://service.civicpdx.org/neighborhood-development/sandbox/foundations/evictionrate/',
    'visualization': 'ChoroplethMap',
  }, 
}

package_info = {
    'packages' : packages,
    'slides' : slides,
    'foundations' : foundations
    }
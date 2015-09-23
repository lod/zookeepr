product_categories = ${h.json.dumps(c.js_categories)|n};
product_includes = ${h.json.dumps(c.js_includes)|n};
products = ${h.json.dumps(c.js_products)|n};

function to_id(str) {
  str = str.toLowerCase();
  str = str.replace(/[\s-]/g, "_");
  str = str.replace(/\W/g, "");
  return str;
}

function cost2nice(cost) {
  return "$"+parseFloat(cost/100).toFixed(2);
}


// Functions to build product groups
function build_radio_product_group(cat_id) {
  cat_products = product_categories[cat_id]['products'].map(function(a){return products[a]});
  list = jQuery("<ul>");
  cat_products.forEach(function(p){
    input = jQuery("<input type='radio' value='"+p['id']+"' name='products.category_"+product_categories[cat_id]['clean_name']+"' category_id='"+cat_id+"'>")
    label = jQuery("<label>"+p['description']+" - "+cost2nice(p['cost'])+"</label>");
    list.append(jQuery("<li>").append(label.prepend(input)));
  });
  return list;
}

function build_select_product_group(cat_id) {
  category = product_categories[cat_id];
  cat_products = product_categories[cat_id]['products'].map(function(a){return products[a]});
  select = jQuery("<select category_id='"+cat_id+"' name='"+category['clean_name']+"'>");
  cat_products.forEach(function(p){select.append('<option product_id="'+p.id+'" category_id="'+cat_id+'" value="'+p.id+'">'+p['description']+' - '+cost2nice(p['cost'])+'</option>')});
  return select;
}

function build_product_group(cat_id) {
  cat = product_categories[cat_id];
  fset = jQuery("<fieldset id='"+cat['idname']+"'></fieldset>");
  fset.append("<h2>"+cat['name']+"</h2>");
  fset.append("<p>"+cat['description']+"</p>");
  return fset;
}


// Functions to manage the swag list
function load_product_group(category_id, target) {
  //cat_products = product_categories[category]['products'].map(function(a){return products[a]});
  //select = jQuery("<select>");
  //cat_products.forEach(function(p){select.append('<option>'+p['description']+'</option>')});
  // TODO: provided product groups shouldn't have a price attached
  select = build_select_product_group(category_id);
  jQuery(target).append("<div class='form-group'><label>"+product_categories[category_id]['name']+"</label>"+select[0].outerHTML+"</div>");
}

// TODO: Would be nice to hide swag group when there are no entries - or state there are no entries
function init_swag_group(category) {
  group_id = "included_"+category.idname+"_swag_list";
  group = jQuery("<div id='"+group_id+"'></div>");
  group.append("<h3>Provided as part of "+category.name+"</h3>");

  // Check if the group already exists, then insert/replace
  if (jQuery("#"+group_id).length == 0) {
    // TODO: Order the entries by display order
    jQuery("#included_swag_lists").append(group);
  } else {
    jQuery("#"+group_id).replaceWith(group);
  }
  return group;
}

function load_included_swag(product_id, target) {
  for (var category_id in product_includes[product_id]) {
    for (var i = 0; i < product_includes[product_id][category_id]; i++) {
      load_product_group(category_id, target);
    }
  }
  jQuery("#swag_section").show();
}

function add_swag_button(category_id) {
  category = product_categories[category_id];
  button = jQuery("<button type='button' id='swag_add_"+category['idname']+"' category_id='"+category_id+"'>Buy "+category['name']+"</button>");

  button.on('click', function() {
    if (jQuery("#additional_swag_list").children().length == 0) {
      jQuery("#additional_swag_list").append("<h3>Purchased</h3>");
    }
    cat_id = jQuery(this).attr('category_id');
    load_product_group(cat_id, jQuery("#additional_swag_list"));

    // TODO: Each swag item needs a different price row
    jQuery("#additional_swag_list .form-group").last().on("change", update_select_price);
  });

  jQuery("#additional_swag_buttons").append(button);
  jQuery("#swag_section").show();
}


// Functions to manage the price summary
function update_price_total() {
  // Tally up the last column
  total = 0;
  jQuery("#price_tally tbody tr td:last-child").each(
    function(undef,cell){total += parseFloat(cell.textContent)}
  );
  jQuery("#price_total").text(parseFloat(total).toFixed(2));
}

function sort_table_comparator(a_in,b_in) {
  var a = jQuery(a_in); var b = jQuery(b_in);

  // Sort by category display order, then product display order
  var ca = product_categories[a.attr("category_id")].display_order;
  var cb = product_categories[b.attr("category_id")].display_order;
  if (ca > cb) return 1;
  if (ca < cb) return -1;

  // Same category - sort by product
  var pa = products[a.attr("product_id")].display_order;
  var pb = products[b.attr("product_id")].display_order;
  if (pa > pb) return 1;
  if (pa < pb) return -1;

  // Identical item
  return 0;
}

function sort_price_table() {
  var table = jQuery("#price_tally tbody tr");
  var rows = table.toArray().sort(sort_table_comparator);
  for (var i = 0; i < rows.length; i++) jQuery("#price_tally tbody").append(rows[i]);
}

function update_price_row(product_id, description, price, qty) {
  // Update a row if it exists, otherwise create it, delete rows with qty = 0
  if(jQuery("#price_"+product_id).length > 0) {
    // if exists, delete it
    jQuery("#price_"+product_id).remove()
  }

  if(qty > 0) {
    product = products[product_id];
    row = jQuery("<tr product_id='"+product_id+"' category_id='"+product.category+"' id='price_"+product_id+"'>");
    row.append("<td>"+description+"</td>");
    row.append("<td>"+qty+"</td>");
    row.append("<td>"+parseFloat(price/100).toFixed(2)+"</td>");
    row.append("<td>"+parseFloat(qty*price/100).toFixed(2)+"</td>");
    jQuery("#price_tally tbody").append(row);
  }

  sort_price_table();
  update_price_total();
}

function update_text_price() {
  var id = jQuery(this).attr('product_id');
  var product = products[id];
  var category = product_categories[product['category']];
  if (product.cost != 0 || category['invoice_free_products']) {
    update_price_row(id, category.name+" - "+product.description, product.cost, jQuery(this).val());
  }
}

function update_radio_price() {
  var cat_id = jQuery(this).attr('category_id');
  var product_id = jQuery(this).attr('value');
  var product = products[product_id];
  // If it is free and we hide free we need to hide the row
  // This requires deletion, in case we previously had a visible option
  // Easiest way to do this is with a quantity of zero to trigger it
  var qty = product.cost != 0 || product_categories[cat_id]['invoice_free_products'] ? 1 : 0;
  update_price_row("C"+cat_id, product.description, product.cost, qty);
}

function update_checkbox_price() {
  var product_id = jQuery(this).attr('product_id');
  var product = products[product_id];
  var category = product_categories[product['category']];
  var qty = jQuery(this).attr('checked') ? 1 : 0

  if (product.cost != 0 || category['invoice_free_products']) {
    update_price_row(product_id, category.name+" - "+product.description, product.cost, qty);
  }
}

function update_select_price() {
  var category_id = jQuery(this).attr("category_id");
  var product_id = jQuery(this).find(":selected").attr("product_id");
  if (product_id === undefined) {
    // No product_id means it is a dummy entry - clear the inventory (0 qty)
    update_price_row("C"+category_id, "", 0, 0);
  } else {
    var product = products[product_id];
    var category = product_categories[product['category']];
    if (product.cost != 0 || category['invoice_free_products']) {
      update_price_row("C"+category_id, category.name+" - "+product.description, product.cost, 1);
    }
  }
}

// vim: set filetype=javascript:

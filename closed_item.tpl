%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<p>The closed items are as follows:</p>
<table border="1">
%for row in rows:
  <tr>
  %for col in row:
    <td>{{col}}</td>
  %end
  
<td><a href="/edit/{{row[0]}}"><button>Edit</button></a></td>

  </tr>


%end
</table>